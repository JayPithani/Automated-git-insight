# 🤖 Automated Git-Insight
> *Turn your Git history into actionable insights and beautiful PDF reports.*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

## 📌 What is this?
**Automated Git-Insight** is a powerful tool for developers and engineering managers to analyze GitHub repositories. It fetches commit history, classifies changes using AI and Regex, checks coding patterns, and generates a professional **PDF Report** containing:
- 📊 **Visual Analytics**: Coding intensity, LOC changes, and categorized commit distribution.
- 🤖 **AI Summaries**: LLM-generated summaries of your recent work.
- 📈 **Skill Growth**: Analysis of the technologies and patterns you've used.

## 🚀 Features
- **Smart Data Fetching**: Robust GitHub API integration with rate limit handling.
- **Advanced Classification**: Regex-based detection for Conventional Commits (Feat, Fix, Refactor, etc.).
- **Rich Analytics**:
  - 📅 **Coding Intensity**: Heatmap of your most productive hours/days.
  - 📉 **Feature vs Bugfix**: Track stability vs velocity over time.
  - 📝 **LOC Analysis**: Lines of Code Added vs Removed.
- **Professional PDF Reports**: Auto-generated reports ready to share with stakeholders or recruiters.

## 🛠️ Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/JayPithani/Automated-git-insight.git
    cd Automated-git-insight
    ```

2. **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```ini
    GITHUB_TOKEN=your_github_pat_here
    GEMINI_API_KEY=your_gemini_key_here  # If using Gemini
    # OR
    OPENAI_API_KEY=your_openai_key_here  # If using OpenAI
    LLM_PROVIDER=GEMINI  # or OPENAI
    ```

> [!NOTE]
> The project uses the new `google-genai` SDK instead of the deprecated `google-generativeai` library.

## 🔑 API Keys Explained

This project requires **two API keys** that serve different purposes:

| Key | Sidebar Field | Purpose | Free? |
|-----|--------------|---------|-------|
| **GitHub Token** | "Enter Your API" (top) | Fetches commits, repositories, and contributor data from GitHub | ✅ Yes |
| **Gemini / OpenAI Key** | "AI Engine" (bottom) | Powers the AI-generated Monthly Summary and Skill Growth analysis | ✅ Yes (Gemini free tier) |

### GitHub Personal Access Token
- **What it does:** Authenticates with GitHub's API to fetch commit history, repo metadata, and contributor info.
- **Without it:** You're limited to 60 API requests/hour (unauthenticated). With it, you get **5,000 requests/hour**.
- **Required for:** Private repositories.
- **Get it here:** [github.com/settings/tokens](https://github.com/settings/tokens) → Generate new token (classic) → Select `repo` scope.

### Gemini API Key (or OpenAI)
- **What it does:** Calls Google's Gemini LLM to analyze your commit messages and generate human-readable insights.
- **Without it:** Charts and metrics still work, but the **AI Summary** tab will be empty.
- **Get it here:** [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → Click "Create API Key" (no credit card needed).
- **Free tier:** 15 requests/minute, 1 million tokens/day — more than enough for this tool.

> [!TIP]
> You can enter both keys either in the **`.env` file** (persisted) or directly in the **sidebar fields** (per session).

## 💻 How to Run

```bash
python main.py --repo username/repo_name --days 30
```

### Arguments:
- `--repo`: **(Required)** The repository format `username/repo`.
- `--days`: Number of days to look back (default: 30).
- `--output`: Output filename for the PDF (default: `report.pdf`).

### Example:
```bash
python main.py --repo facebook/react --days 14 --output react_report.pdf
```

## 🌐 Web Interface

```bash
streamlit run app.py
```

Features:
- 📊 Interactive dashboard with real-time progress indicators
- 🔍 Analyze single repos or entire GitHub usernames
- 📈 Multiple chart views with tabs
- 🤖 AI-powered insights generation
- 📄 One-click PDF report download

## 🏗️ Project Architecture

```
Automated-git-insight/
├── app.py                  # Streamlit web interface
├── main.py                 # CLI entry point
├── src/
│   ├── github_connector.py # GitHub API with smart rate limiting
│   ├── data_processor.py   # Cleans and classifies commit data
│   ├── visualizer.py       # Generates charts (Matplotlib/Seaborn)
│   ├── llm_analyzer.py     # Connects to LLM for insights
│   └── report_generator.py # Dynamic PDF with data-driven descriptions
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```