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

st.set_page_config(page_title="Git-Insight", page_icon="🔍", layout="wide")
os.makedirs("output", exist_ok=True)

for key, val in [('analysis_done', False), ('clean_df', None), ('summary', ''), ('skill_growth', '')]:
    if key not in st.session_state:
        st.session_state[key] = val

def load_css():
    css = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>

html, body, [class*="css"], .stApp, p, li, span, div, label, button {
    font-family: 'Inter', sans-serif !important;
}
h1 {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #2C1810 !important;
}
h2, h3, h4 {
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    color: #3D2214 !important;
}

/* ── TOOLBAR white ── */
header[data-testid="stHeader"],
header[data-testid="stHeader"] > div,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border-bottom: 1px solid #E8E0DC !important;
}
header[data-testid="stHeader"] svg { fill: #5C3D2E !important; }
#MainMenu, footer, [data-testid="stFooter"], [class*="footer"] { visibility: hidden !important; display: none !important; }
button[kind="header"],
[data-testid="baseButton-header"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E8E0DC !important;
    border-radius: 6px !important;
    color: #5C3D2E !important;
}

/* ── MAIN AREA — off white ── */
.stApp { background-color: #FAF9F7 !important; }
.main .block-container {
    background-color: #FAF9F7 !important;
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* ── SIDEBAR — reddish brown ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
section[data-testid="stSidebar"] > div > div > div,
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div:first-child {
    background-color: #6B2D1F !important;
    background: #6B2D1F !important;
    border-right: none !important;
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
    border-radius: 10px !important;
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
    border: 1.5px solid #E8E0DC !important;
    border-radius: 10px !important;
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
    border: 1.5px solid #E8E0DC !important;
    border-radius: 10px !important;
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
    border: 1.5px solid #E8E0DC !important;
    border-radius: 10px !important;
    color: #2C1810 !important;
}

/* ── BUTTONS — use brown accent ── */
.stButton > button {
    background-color: #6B2D1F !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 28px !important;
}
.stButton > button:hover {
    background-color: #5A2419 !important;
    color: #FFFFFF !important;
}
.stDownloadButton > button {
    background-color: #10B981 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}

/* ── METRIC CARDS ── */
[data-testid="metric-container"],
div[data-testid="metric-container"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1.5px solid #E8D5CF !important;
    border-radius: 14px !important;
    padding: 18px !important;
    box-shadow: 0 1px 4px rgba(107,45,31,0.06) !important;
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
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    font-family: Sora, sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
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
    background-color: transparent !important;
    border-bottom: 1.5px solid #E8E0DC !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #B08070 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #6B2D1F !important;
    border-bottom: 2px solid #6B2D1F !important;
    background-color: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid #E8E0DC !important;
    border-top: none !important;
    border-radius: 0 0 14px 14px !important;
    padding: 22px !important;
}

/* ── MISC ── */
.stAlert { border-radius: 10px !important; }
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid #E8E0DC !important;
}
hr { border-color: #E8E0DC !important; }
[data-testid="stProgressBar"] > div > div {
    background-color: #6B2D1F !important;
}

</style>
"""
    try:
        st.html(css)
    except AttributeError:
        st.markdown(css, unsafe_allow_html=True)

load_css()

# Remove keyboard_double button via JS
_js_hide_keyboard = """
<script>
function removeKeyboardBtn() {
    var btns = document.querySelectorAll('button');
    btns.forEach(function(btn) {
        var label = btn.getAttribute('aria-label') || '';
        if (label === 'keyboard_double_a' || label === 'keyboard_double_arrow_right' || label === 'keyboard_double_arrow_left') {
            btn.style.display = 'none';
            btn.style.width = '0';
            btn.style.height = '0';
            btn.style.overflow = 'hidden';
            btn.style.position = 'absolute';
        }
    });
}
removeKeyboardBtn();
setInterval(removeKeyboardBtn, 300);
</script>
"""
st.components.v1.html(_js_hide_keyboard, height=0)

# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;padding:10px 0 24px;">'
        '<div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.15);'
        'flex-shrink:0;display:flex;align-items:center;justify-content:center;">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none"'
        ' stroke="white" stroke-width="2.2" stroke-linecap="round">'
        '<circle cx="12" cy="12" r="4"/>'
        '<path d="M12 2v2M12 20v2M2 12h2M20 12h2'
        ' M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41'
        ' M17.66 6.34l-1.41 1.41M6.34 17.66l-1.41 1.41"/>'
        '</svg></div>'
        '<div>'
        '<div style="font-family:Sora,sans-serif;font-size:16px;font-weight:700;color:#FFFFFF;">Git-Insight</div>'
        '<div style="font-family:Inter,sans-serif;font-size:11px;color:#F0C4B4;margin-top:1px;">Repository Analytics</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;'
        'color:#F0C4B4;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">'
        '🔐 Authentication</div>',
        unsafe_allow_html=True
    )
    load_dotenv()
    env_token = os.getenv("GITHUB_TOKEN", "")
    token = st.text_input("gh_token", value=env_token, type="password",
                          placeholder="GitHub Personal Access Token",
                          label_visibility="collapsed",
                          help="Required for private repos or high API limits")

    st.markdown(
        '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;'
        'color:#F0C4B4;letter-spacing:0.1em;text-transform:uppercase;'
        'margin:18px 0 6px;">🤖 AI Configuration</div>',
        unsafe_allow_html=True
    )
    llm_provider = st.selectbox("provider", ["GEMINI", "OPENAI"], index=0,
                                label_visibility="collapsed")
    api_key = st.text_input("api_key", type="password",
                            placeholder=f"{llm_provider} API Key",
                            label_visibility="collapsed")

    if token:   os.environ["GITHUB_TOKEN"]            = token
    if api_key: os.environ[f"{llm_provider}_API_KEY"] = api_key
    os.environ["LLM_PROVIDER"] = llm_provider

    st.markdown(
        '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;'
        'color:#F0C4B4;letter-spacing:0.1em;text-transform:uppercase;'
        'margin:18px 0 8px;">💡 Quick Examples</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:6px;">'
        '<span style="font-family:monospace;font-size:11px;padding:4px 10px;border-radius:6px;'
        'background:rgba(255,255,255,0.12);color:#FFFFFF;border:1px solid rgba(255,255,255,0.2);">'
        'streamlit/streamlit</span>'
        '<span style="font-family:monospace;font-size:11px;padding:4px 10px;border-radius:6px;'
        'background:rgba(255,255,255,0.12);color:#FFFFFF;border:1px solid rgba(255,255,255,0.2);">'
        'facebook/react</span>'
        '<span style="font-family:monospace;font-size:11px;padding:4px 10px;border-radius:6px;'
        'background:rgba(255,255,255,0.12);color:#FFFFFF;border:1px solid rgba(255,255,255,0.2);">'
        'JayPithani</span>'
        '</div>',
        unsafe_allow_html=True
    )


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
st.markdown(
    '<h1 style="font-family:Sora,sans-serif;font-size:28px;font-weight:700;'
    'color:#2C1810;margin:0 0 6px;">Repository Analysis</h1>'
    '<p style="font-family:Inter,sans-serif;font-size:14px;color:#9B6B5A;margin:0;">'
    'Analyze commit history, get AI summaries, and visualize your coding patterns.</p>',
    unsafe_allow_html=True
)
st.markdown("<hr style='margin:16px 0 20px;'>", unsafe_allow_html=True)

# Search row
col1, col2 = st.columns([4, 1])
with col1:
    repo_input = st.text_input("repo", placeholder="owner/repo  or  username",
                               label_visibility="collapsed")
with col2:
    days = st.number_input("Days", min_value=7, max_value=3650, value=30,
                           label_visibility="collapsed")

col_btn, col_hint = st.columns([1, 3])
with col_btn:
    start_clicked = st.button("🔍  Analyze Repository")
with col_hint:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:8px;margin-top:9px;flex-wrap:wrap;">'
        '<span style="font-family:Inter,sans-serif;font-size:12px;color:#B08070;">Try:</span>'
        '<span style="font-family:monospace;font-size:11px;background:#F5EDE9;color:#6B2D1F;'
        'padding:3px 8px;border-radius:5px;border:1px solid #E8D5CF;">streamlit/streamlit</span>'
        '<span style="color:#D4B5AB;">|</span>'
        '<span style="font-family:monospace;font-size:11px;background:#F5EDE9;color:#6B2D1F;'
        'padding:3px 8px;border-radius:5px;border:1px solid #E8D5CF;">facebook/react</span>'
        '<span style="color:#D4B5AB;">|</span>'
        '<span style="font-family:monospace;font-size:11px;background:#F5EDE9;color:#6B2D1F;'
        'padding:3px 8px;border-radius:5px;border:1px solid #E8D5CF;">JayPithani</span>'
        '<span style="font-family:Inter,sans-serif;font-size:12px;color:#B08070;">(username)</span>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)

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
            since_date = datetime.now() - timedelta(days=days)

            if "/" in repo_input:
                if repo_input.count("/") != 1:
                    st.error("⚠️ Invalid format. Use 'owner/repo'.")
                    st.stop()
                status_text.text("📥 Fetching commits...")
                progress_bar.progress(20)
                df = connector.fetch_commits(repo_input, since=since_date)
            else:
                status_text.text(f"🔍 Finding repositories for '{repo_input}'...")
                progress_bar.progress(10)
                repos = connector.get_user_repositories(repo_input)
                if not repos:
                    st.error(f"❌ No repositories found for '{repo_input}'.")
                    st.stop()
                st.info(f"📦 Found **{len(repos)}** repositories. Fetching commits…")
                all_commits = []
                for idx, repo in enumerate(repos):
                    pct = 10 + int(60 * (idx + 1) / len(repos))
                    status_text.text(f"📥 [{idx+1}/{len(repos)}] {repo}…")
                    progress_bar.progress(pct)
                    try:
                        repo_df = connector.fetch_commits(repo, since=since_date)
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
        '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;'
        'color:#B08070;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:14px;">'
        'Overview</div>',
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
                '<div style="background:#FDF6F4;border:1.5px solid #F0D0C8;border-radius:12px;padding:16px 18px;">'
                '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;color:#6B2D1F;'
                'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Monthly Summary</div>'
                '</div>',
                unsafe_allow_html=True
            )
            st.write(summary)
        with col_b:
            st.markdown(
                '<div style="background:#F5EDE9;border:1.5px solid #E8D5CF;border-radius:12px;padding:16px 18px;">'
                '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;color:#8B3A28;'
                'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Skill Growth</div>'
                '</div>',
                unsafe_allow_html=True
            )
            st.write(skill_growth)

    st.markdown("<hr style='margin:28px 0;'>", unsafe_allow_html=True)

    st.markdown(
        '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:600;'
        'color:#B08070;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:14px;">'
        'Export Report</div>',
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