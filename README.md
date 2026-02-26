# 🤖 Automated Git-Insight
> *Turn your Git history into actionable insights and beautiful PDF reports.*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

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

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/insight-git.git
    cd insight-git
    ```

2.  **Create a Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```ini
    GITHUB_TOKEN=your_github_pat_here
    GEMINI_API_KEY=your_gemini_key_here  # If using Gemini for LLM
    # OR
    OPENAI_API_KEY=your_openai_key_here  # If using OpenAI for LLM
    LLM_PROVIDER=GEMINI  # or OPENAI
    ```

> [!NOTE]
> The project now uses the new `google-genai` SDK instead of the deprecated `google-generativeai` library.

## 💻 How to Run

Run the tool from the command line:

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

## 🏗️ Project Architecture
The project follows a modular architecture:

```
insight-git/
├── main.py                 # Entry point
├── src/
│   ├── github_connector.py # Handles GitHub API interactions
│   ├── data_processor.py   # Cleans and classifies commit data
│   ├── visualizer.py       # Generates charts (Matplotlib/Seaborn)
│   ├── llm_analyzer.py     # Connects to LLM for insights
│   └── report_generator.py # Compiles everything into a PDF
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

## 🌐 Web Interface

The project includes a beautiful Streamlit web interface for easy interaction:

```bash
streamlit run app.py
```

Features:
- 📊 Interactive dashboard with real-time progress indicators
- 🔍 Input validation and helpful error messages
- 📈 Multiple chart views with tabs
- 🤖 AI-powered insights generation
- 📄 One-click PDF report download

## 📸 Screenshots

### Dashboard
> *Screenshots coming soon - run the app and capture your own!*

### Charts & Analytics
> *Screenshots coming soon - run the app and capture your own!*

<!-- To add screenshots:
1. Run: streamlit run app.py
2. Capture screenshots of dashboard and charts
3. Save in assets/ folder
4. Update this section with: ![Description](assets/filename.png)
-->

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License
MIT License
