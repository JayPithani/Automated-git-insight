import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.github_connector import GithubConnector
from src.data_processor import DataProcessor
from src.llm_analyzer import LLMAnalyzer
from src.visualizer import Visualizer
from src.report_generator import ReportGenerator

# --- Page Config & Setup ---
st.set_page_config(page_title="Git-Insight", page_icon="🤖", layout="wide")

# Ensure the output directory exists so the Visualizer doesn't crash
os.makedirs("output", exist_ok=True)

# Initialize Session State Variables
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'clean_df' not in st.session_state:
    st.session_state.clean_df = None
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'skill_growth' not in st.session_state:
    st.session_state.skill_growth = ""

def load_css():
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #ff4b4b;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- Sidebar ---
with st.sidebar:
    st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=50)
    st.title("⚙️ Settings")

    st.markdown("### 🔐 Authentication")

    load_dotenv()
    env_token = os.getenv("GITHUB_TOKEN", "")

    token = st.text_input("GitHub Token", value=env_token, type="password",
                          help="Required for private repos or high limits")

    st.markdown("---")
    st.markdown("### 🤖 AI Configuration")

    llm_provider = st.selectbox("Provider", ["GEMINI", "OPENAI"], index=0)
    api_key = st.text_input(f"{llm_provider} API Key", type="password")

    if token:
        os.environ["GITHUB_TOKEN"] = token
    if api_key:
        os.environ[f"{llm_provider}_API_KEY"] = api_key
    os.environ["LLM_PROVIDER"] = llm_provider

# --- Main App ---
st.title("🤖 Automated Git-Insight")
st.markdown("Analyze your GitHub repository history, get AI summaries, and visualize your coding patterns.")
st.markdown("---")

st.info("👋 Enter a repository name and click **Start Analysis** to generate insights.")

col1, col2 = st.columns([3, 1])
with col1:
    repo_name = st.text_input("Repository Name (e.g., facebook/react)", placeholder="owner/repo")
with col2:
    days = st.number_input("Days to Analyze", min_value=7, max_value=3650, value=30)

st.markdown("**Try Examples:** `streamlit/streamlit` | `facebook/react` | `microsoft/vscode`")

# --- Step 1: Data Fetching & Processing (Only runs when button is clicked) ---
if st.button("🚀 Start Analysis"):
    if not repo_name:
        st.error("⚠️ Please enter a repository name.")
    elif "/" not in repo_name or repo_name.count("/") != 1:
        st.error("⚠️ Invalid repository format. Please use 'owner/repo'.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("🔍 Validating repository...")
            progress_bar.progress(10)

            connector = GithubConnector(token if token else None)
            since_date = datetime.now() - timedelta(days=days)

            status_text.text("📥 Fetching commits...")
            progress_bar.progress(20)

            df = connector.fetch_commits(repo_name, since=since_date)

            if df.empty:
                st.error("❌ No commits found or API limit reached.")
            else:
                st.success(f"✅ Fetched {len(df)} commits!")

                status_text.text("⚙️ Processing data...")
                progress_bar.progress(40)

                processor = DataProcessor(df)
                clean_df = processor.process()

                status_text.text("🤖 Running AI analysis...")
                progress_bar.progress(70)

                llm = LLMAnalyzer()
                summary = llm.summarize_commits(clean_df['message'].tolist())
                categories = clean_df['category'].value_counts().to_string()
                skill_growth = llm.analyze_skill_growth(f"Commit Categories Distribution:\n{categories}")

                # SAVE TO SESSION STATE
                st.session_state.clean_df = clean_df
                st.session_state.summary = summary
                st.session_state.skill_growth = skill_growth
                st.session_state.analysis_done = True

                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")

        except Exception as e:
            st.error(f"❌ Error: {e}")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()


# --- Step 2: UI Rendering & PDF Generation (Runs if data exists in memory) ---
if st.session_state.analysis_done:
    
    # Load data from memory
    clean_df = st.session_state.clean_df
    summary = st.session_state.summary
    skill_growth = st.session_state.skill_growth

    st.markdown("### 📊 Overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📌 Total Commits", len(clean_df))
    m2.metric("👥 Contributors", clean_df['author'].nunique())
    if 'additions' in clean_df.columns:
        m3.metric("📥 LOC Added", clean_df['additions'].sum())
        m4.metric("📤 LOC Deleted", clean_df['deletions'].sum())

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Commit Activity", "🧩 Categories", "🔥 Intensity", "🤖 AI Summary"]
    )

    viz = Visualizer(clean_df)

    with tab1:
        path = viz.plot_commits_over_time()
        if path: st.image(path)

    with tab2:
        path = viz.plot_category_distribution()
        if path: st.image(path)

    with tab3:
        path = viz.plot_coding_intensity()
        if path: st.image(path)

    with tab4:
        st.markdown("#### 📝 Monthly Summary")
        st.success(summary)

        st.markdown("#### 🚀 Skill Growth")
        st.success(skill_growth)

    st.markdown("---")

    # PDF Button is now safely isolated from the main analysis block
    if st.button("📄 Generate & Download PDF Report"):
        with st.spinner("📄 Creating PDF report... Please wait."):
            try:
                report = ReportGenerator()
                
                # Gather all generated plots to pass into the PDF
                plots = {
                    "Commit Activity": os.path.join("output", "commits_over_time.png"),
                    "Category Distribution": os.path.join("output", "category_distribution.png"),
                    "Coding Intensity": os.path.join("output", "coding_intensity.png")
                }
                # Ensure we only pass images that actually exist
                existing_plots = {k: v for k, v in plots.items() if os.path.exists(v)}
                
                report.generate_report(summary, skill_growth, existing_plots, output_file="git_insight_report.pdf")

                with open("git_insight_report.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()

                st.success("📄 Report Generated Successfully!")
                st.download_button(
                    label="📥 Download PDF",
                    data=PDFbyte,
                    file_name="git_insight_report.pdf",
                    mime='application/octet-stream'
                )
            except Exception as e:
                st.error(f"❌ Failed to generate PDF: {e}")

st.markdown("---")
st.caption("Made with ❤️ using Python & AI")