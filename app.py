import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from src.github_connector import GithubConnector
from src.data_processor import DataProcessor
from src.llm_analyzer import LLMAnalyzer
from src.visualizer import Visualizer
from src.report_generator import ReportGenerator

st.set_page_config(page_title="Git-Insight", page_icon="🔍", layout="wide")
os.makedirs("output", exist_ok=True)

for key, val in [('analysis_done', False), ('clean_df', None), ('summary', ''), ('skill_growth', '')]:
    if key not in st.session_state:
        st.session_state[key] = val

def load_css():
    css = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>

html, body, [class*="css"], .stApp, p, li, span, div, label, button {
    font-family: 'Inter', sans-serif !important;
}
h1, h2, h3, h4 {
    font-family: 'Sora', sans-serif !important;
    color: #2C1810 !important;
    letter-spacing: 0 !important;
}
h1 { font-weight: 800 !important; }
h2, h3, h4 { font-weight: 700 !important; }

/* ── TOOLBAR white ── */
header[data-testid="stHeader"],
header[data-testid="stHeader"] > div,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    background: #FAF9F7 !important;
    border-bottom: 1px solid #E8E0DC !important;
}
#MainMenu, footer, [data-testid="stFooter"], [class*="footer"],
button[kind="header"], [data-testid="baseButton-header"] {
    visibility: hidden !important;
    display: none !important;
}

/* ── MAIN AREA — off white ── */
.stApp { background-color: #FAF9F7 !important; }
.main .block-container {
    background-color: #FAF9F7 !important;
    padding-top: 1.8rem;
    padding-bottom: 2.4rem;
    max-width: 1180px;
}

/* ── SIDEBAR — reddish brown ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] > div > div > div,
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div:first-child {
    background: #6B2D1F !important;
    border-right: none !important;
    overflow-x: hidden !important;
}

/* Sidebar text colors — light on dark */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown {
    color: #F5E6E0 !important;
}
[data-testid="stSidebar"] strong {
    color: #FFFFFF !important;
}

/* Sidebar inputs — slightly lighter brown */
[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #7D3624 !important;
    border: 1px solid #9B4A35 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
    color: #C4897A !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: #F5C6B4 !important;
    box-shadow: 0 0 0 2px rgba(245,198,180,0.2) !important;
}

input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear { display: none !important; }
[data-testid="stSidebar"] .stTextInput input {
    background-color: #7D3624 !important;
    color: #FFFFFF !important;
    border: 1px solid #9B4A35 !important;
    caret-color: #FFFFFF !important;
}

/* ── MAIN INPUTS ── */
.stTextInput > div > div > input {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E0DC !important;
    border-radius: 8px !important;
    color: #2C1810 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6B2D1F !important;
    box-shadow: 0 0 0 3px rgba(107,45,31,0.12) !important;
}

/* ── NUMBER INPUT white ── */
div[data-testid="stNumberInput"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E0DC !important;
    border-radius: 8px !important;
    overflow: hidden;
}
div[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #2C1810 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stNumberInput"] button {
    background-color: #F5EDE9 !important;
    color: #6B2D1F !important;
    border: none !important;
    border-left: 1px solid #E8E0DC !important;
}
div[data-testid="stNumberInput"] button:hover {
    background-color: #EDDED9 !important;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E0DC !important;
    border-radius: 8px !important;
    color: #2C1810 !important;
}

/* ── BUTTONS — use brown accent ── */
.stButton > button {
    background-color: #6B2D1F !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    padding: 10px 28px !important;
}
.stButton > button:hover {
    background-color: #5A2419 !important;
    color: #FFFFFF !important;
}
.stDownloadButton > button {
    background-color: #8B3A28 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

/* ── METRIC CARDS ── */
[data-testid="metric-container"],
div[data-testid="metric-container"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #E8D5CF !important;
    border-radius: 8px !important;
    padding: 18px !important;
    box-shadow: 0 12px 26px rgba(24,32,42,0.06) !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] div {
    font-family: Inter, sans-serif !important;
    font-size: 11px !important;
    color: #9B6B5A !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    font-family: Sora, sans-serif !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #2C1810 !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stMetricDelta"] {
    visibility: visible !important;
    opacity: 1 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #F5EDE9 !important;
    border: 1px solid #E8E0DC !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #B08070 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    padding: 9px 16px !important;
    border-radius: 6px !important;
}
.stTabs [aria-selected="true"] {
    color: #2C1810 !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 6px 16px rgba(24,32,42,0.08) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E8D5CF !important;
    border-radius: 8px !important;
    margin-top: 12px !important;
    padding: 22px !important;
}

/* ── MISC ── */
.stAlert { border-radius: 8px !important; }
.stAlert p, .stAlert span, .stAlert div,
[data-testid="stAlert"] p, [data-testid="stAlert"] span, [data-testid="stAlert"] div,
[role="alert"] p, [role="alert"] span, [role="alert"] div {
    color: #2C1810 !important;
}
[data-testid="stImage"] img {
    border-radius: 8px !important;
    border: 1px solid #E8D5CF !important;
}
hr { border-color: #E8D5CF !important; }
[data-testid="stProgressBar"] > div > div {
    background-color: #6B2D1F !important;
}

.gi-hero {
    background: #FFFFFF;
    border: 1px solid #E8D5CF;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 18px 42px rgba(24,32,42,0.07);
    margin-bottom: 18px;
}
.gi-kicker, .gi-section-label, .gi-sidebar-label {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.gi-kicker { color: #6B2D1F; margin-bottom: 8px; }
.gi-title {
    color: #2C1810;
    font-family: Sora, sans-serif;
    font-size: 34px;
    font-weight: 800;
    line-height: 1.08;
    margin: 0 0 8px;
}
.gi-subtitle {
    color: #B08070;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
    max-width: 720px;
}
.gi-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.gi-chip {
    background: #F5EDE9;
    border: 1px solid #E8D5CF;
    border-radius: 999px;
    color: #6B2D1F;
    font-size: 12px;
    font-weight: 800;
    padding: 7px 10px;
}
.gi-chip strong { color: #8B3A28; }
.gi-panel {
    background: #FFFFFF;
    border: 1px solid #E8D5CF;
    border-radius: 8px;
    padding: 18px;
    box-shadow: 0 12px 28px rgba(24,32,42,0.05);
}
.gi-section-label { color: #9B6B5A; margin: 4px 0 14px; }
.gi-sidebar-card {
    background: #7D3624;
    border: 1px solid #9B4A35;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0 18px;
}
.gi-sidebar-icon {
    align-items: center;
    background: #6B2D1F;
    border-radius: 8px;
    display: flex;
    height: 42px;
    justify-content: center;
    width: 42px;
}
.gi-sidebar-title {
    color: #FFFFFF;
    font-family: Sora, sans-serif;
    font-size: 18px;
    font-weight: 800;
    margin-top: 12px;
}
.gi-sidebar-subtitle { color: #F0C4B4; font-size: 12px; margin-top: 3px; }
.gi-sidebar-label { color: #F0C4B4; margin: 18px 0 7px; }
.gi-note {
    border-left: 3px solid #8B3A28;
    color: #F0C4B4;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 18px;
    padding-left: 10px;
}

[data-testid="stSidebarHeader"], [data-testid="stSidebarHeader"] *,
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"], [data-testid="collapsedControl"] *,
button[aria-label*="keyboard_double"],
[data-testid="stSidebar"] button:has(.material-symbols-rounded),
[data-testid="stSidebar"] button:has(.material-symbols-outlined) {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
}

</style>
"""
    try:
        st.html(css)
    except AttributeError:
        st.markdown(css, unsafe_allow_html=True)

load_css()

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="gi-sidebar-card">'
        '<div class="gi-sidebar-icon">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4 7h16M4 12h10M4 17h7"/>'
        '<path d="M17 14l3 3-3 3"/>'
        '</svg></div>'
        '<div class="gi-sidebar-title">Git-Insight</div>'
        '<div class="gi-sidebar-subtitle">Repository intelligence dashboard</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="gi-sidebar-label">Enter Your API</div>', unsafe_allow_html=True)
    load_dotenv()
    token = st.text_input("gh_token", value="", type="password",
                          placeholder="GitHub personal access token",
                          label_visibility="collapsed",
                          help="Required for private repos or high API limits")

    st.markdown('<div class="gi-sidebar-label">AI Engine</div>', unsafe_allow_html=True)
    llm_provider = st.selectbox("provider", ["GEMINI", "OPENAI"], index=0,
                                label_visibility="collapsed")
    api_key = st.text_input("api_key", type="password",
                            placeholder=f"{llm_provider} API key",
                            label_visibility="collapsed")

    st.markdown(
        '<div class="gi-note">Add keys once, then analyze any public repository or GitHub username from the workbench.</div>',
        unsafe_allow_html=True
    )

    if token:   os.environ["GITHUB_TOKEN"]            = token
    if api_key: os.environ[f"{llm_provider}_API_KEY"] = api_key
    os.environ["LLM_PROVIDER"] = llm_provider


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
st.markdown(
    '<div class="gi-hero">'
    '<div class="gi-kicker">Repository Analytics</div>'
    '<div class="gi-title">Understand a codebase from its commit trail.</div>'
    '<p class="gi-subtitle">Analyze commit cadence, contribution patterns, message categories, and AI-generated engineering insights from a repository or a full GitHub profile.</p>'
    '<div class="gi-chips">'
    '<span class="gi-chip"><strong>01</strong> Fetch commits</span>'
    '<span class="gi-chip"><strong>02</strong> Classify work</span>'
    '<span class="gi-chip"><strong>03</strong> Export PDF</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="gi-section-label">Analysis Workbench</div>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    repo_input = st.text_input("repo", placeholder="owner/repo or GitHub username",
                               label_visibility="collapsed")
with col2:
    days = st.number_input("Days", min_value=7, max_value=3650, value=30,
                           label_visibility="collapsed")

col_btn, col_hint = st.columns([1.35, 3])
with col_btn:
    start_clicked = st.button("Analyze Repository")

st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# STEP 1
# -------------------------------------------------------------------
if start_clicked:
    if not repo_input:
        st.error("⚠️ Please enter a repository name or GitHub username.")
    else:
        progress_bar = st.progress(0)
        status_text  = st.empty()
        try:
            connector  = GithubConnector(token if token else None)
            since_date = datetime.now(timezone.utc) - timedelta(days=days)

            if "/" in repo_input:
                if repo_input.count("/") != 1:
                    st.error("⚠️ Invalid format. Use 'owner/repo'.")
                    st.stop()
                status_text.text("📥 Fetching commits...")
                progress_bar.progress(20)
                df = connector.fetch_commits(repo_input, since=since_date, max_commits=500)
            else:
                status_text.text(f"🔍 Finding repositories for '{repo_input}'...")
                progress_bar.progress(10)
                repos = connector.get_user_repositories(repo_input, pushed_since=since_date)
                if not repos:
                    st.error(f"❌ No repositories found for '{repo_input}'.")
                    st.stop()
                st.info(f"📦 Found **{len(repos)}** repositories. Fetching commits…")
                max_commits_per_repo = max(10, min(75, 500 // len(repos)))
                st.caption(f"Scanning recently pushed non-fork repositories, max {max_commits_per_repo} commits each.")
                all_commits = []
                for idx, repo in enumerate(repos):
                    pct = 10 + int(60 * (idx + 1) / len(repos))
                    status_text.text(f"📥 [{idx+1}/{len(repos)}] {repo}…")
                    progress_bar.progress(pct)
                    try:
                        repo_df = connector.fetch_commits(
                            repo,
                            since=since_date,
                            max_commits=max_commits_per_repo
                        )
                        if not repo_df.empty:
                            repo_df['repository'] = repo
                            all_commits.append(repo_df)
                    except Exception as repo_err:
                        st.warning(f"⚠️ Skipped {repo}: {repo_err}")
                df = pd.concat(all_commits, ignore_index=True) if all_commits else pd.DataFrame()

            if df.empty:
                st.error("❌ No commits found or API limit reached.")
            else:
                st.success(f"✅ Fetched **{len(df)}** commits!")
                status_text.text("⚙️ Processing data…")
                progress_bar.progress(80)
                processor = DataProcessor(df)
                clean_df  = processor.process()
                status_text.text("🤖 Running AI analysis…")
                progress_bar.progress(90)
                llm          = LLMAnalyzer()
                summary      = llm.summarize_commits(clean_df['message'].tolist())
                categories   = clean_df['category'].value_counts().to_string()
                skill_growth = llm.analyze_skill_growth(
                    f"Commit Categories Distribution:\n{categories}")
                st.session_state.clean_df     = clean_df
                st.session_state.summary      = summary
                st.session_state.skill_growth = skill_growth
                st.session_state.analysis_done = True
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
        except Exception as e:
            st.error(f"❌ Error: {e}")
        progress_bar.empty()
        status_text.empty()

# -------------------------------------------------------------------
# STEP 2
# -------------------------------------------------------------------
if st.session_state.analysis_done:
    clean_df     = st.session_state.clean_df
    summary      = st.session_state.summary
    skill_growth = st.session_state.skill_growth

    st.markdown(
        '<div class="gi-section-label">Overview</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Commits",  f"{len(clean_df):,}")
    m2.metric("Contributors",   clean_df['author'].nunique())
    if 'additions' in clean_df.columns:
        m3.metric("Lines Added", f"+{clean_df['additions'].sum():,}")
        net = clean_df['additions'].sum() - clean_df['deletions'].sum()
        m4.metric("Lines Removed", f"−{clean_df['deletions'].sum():,}",
                  delta=f"net {'+' if net >= 0 else ''}{net:,}",
                  delta_color="normal")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈  Commit Activity", "🧩  Categories",
        "🔥  Intensity",       "🤖  AI Summary"
    ])
    viz = Visualizer(clean_df)

    with tab1:
        st.caption("Daily commit frequency over the selected period.")
        path = viz.plot_commits_over_time()
        if path: st.image(path, use_column_width=True)

    with tab2:
        st.caption("Breakdown of commit types based on message patterns.")
        path = viz.plot_category_distribution()
        if path: st.image(path, use_column_width=True)

    with tab3:
        st.caption("Your most productive hours and days of the week.")
        path = viz.plot_coding_intensity()
        if path: st.image(path, use_column_width=True)

    with tab4:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                '<div class="gi-panel" style="box-shadow:none;margin-bottom:10px;">'
                '<div class="gi-section-label" style="margin-bottom:0;">Monthly Summary</div>'
                '</div>',
                unsafe_allow_html=True
            )
            if summary and summary.startswith("Error"):
                st.warning(summary)
            elif summary:
                st.write(summary)
            else:
                st.info("No AI summary available. Check your Gemini API key.")
        with col_b:
            st.markdown(
                '<div class="gi-panel" style="box-shadow:none;margin-bottom:10px;">'
                '<div class="gi-section-label" style="margin-bottom:0;">Skill Growth</div>'
                '</div>',
                unsafe_allow_html=True
            )
            if skill_growth and skill_growth.startswith("Error"):
                st.warning(skill_growth)
            elif skill_growth:
                st.write(skill_growth)
            else:
                st.info("No skill analysis available. Check your Gemini API key.")

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown(
        '<div class="gi-section-label">Export Report</div>',
        unsafe_allow_html=True
    )

    col_pdf, _ = st.columns([1, 3])
    with col_pdf:
        if st.button("📄  Generate PDF Report"):
            with st.spinner("Creating your PDF report…"):
                try:
                    report = ReportGenerator(df=clean_df)
                    plots  = {
                        "Commit Activity":       os.path.join("output", "commits_over_time.png"),
                        "Category Distribution": os.path.join("output", "category_distribution.png"),
                        "Coding Intensity":      os.path.join("output", "coding_intensity.png"),
                    }
                    existing_plots = {k: v for k, v in plots.items() if os.path.exists(v)}
                    report.generate_report(summary, skill_growth, existing_plots,
                                           output_file="git_insight_report.pdf")
                    with open("git_insight_report.pdf", "rb") as f:
                        PDFbyte = f.read()
                    st.success("✅ Report ready!")
                    st.download_button(label="📥  Download PDF", data=PDFbyte,
                                       file_name="git_insight_report.pdf",
                                       mime="application/octet-stream")
                except Exception as e:
                    st.error(f"❌ Failed to generate PDF: {e}")
