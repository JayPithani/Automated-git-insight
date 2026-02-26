# Instructions for Completing Manual Tasks

This guide helps you complete the remaining manual tasks that require running the application.

## Prerequisites

Before running these tasks, make sure you've installed the updated dependencies:

```bash
pip install -r requirements.txt
```

**Important**: The project now uses `google-genai` (not `google-generativeai`). If you had the old library installed, you may want to uninstall it first:

```bash
pip uninstall google-generativeai
pip install google-genai
```

## Task 1: Generate Sample PDF Report

1. **Set up your environment variables** in `.env`:
   ```ini
   GITHUB_TOKEN=your_github_token_here
   GEMINI_API_KEY=your_gemini_api_key_here  # or OPENAI_API_KEY
   LLM_PROVIDER=GEMINI  # or OPENAI
   ```

2. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

3. **Generate a report**:
   - Enter a well-known public repository (suggestions: `streamlit/streamlit`, `microsoft/vscode`, `facebook/react`)
   - Set days to 30-90 for meaningful data
   - Click "🚀 Analyze Repository"
   - Wait for analysis to complete
   - Click "📄 Generate & Download PDF Report"
   - Save the downloaded PDF

4. **Add PDF to the repo**:
   - Move the downloaded `git_insight_report.pdf` to the `examples/` folder
   - Rename it to be descriptive, e.g., `examples/streamlit_30day_report.pdf`

## Task 2: Capture Screenshots

While the Streamlit app is running with analysis results:

### Screenshot 1: Dashboard Overview
1. Show the main interface with:
   - Sidebar with settings
   - Repository input field
   - Overview metrics (Total Commits, Authors, LOC Added/Deleted)
2. Use a screenshot tool (Windows: Win+Shift+S, Mac: Cmd+Shift+4)
3. Save as `assets/dashboard.png`

### Screenshot 2: Commit Activity Chart
1. Navigate to the "📈 Commit Activity" tab
2. Capture the commit over time chart
3. Save as `assets/commit_activity.png`

### Screenshot 3: Coding Intensity Heatmap
1. Navigate to the "🔥 Intensity" tab
2. Capture the coding intensity heatmap
3. Save as `assets/coding_intensity.png`

## Task 3: Update README with Screenshots

Once you have the screenshots, update the README.md file:

1. Open `README.md`
2. Find the "📸 Screenshots" section
3. Replace the placeholder text with actual image links:

```markdown
## 📸 Screenshots

### Dashboard
![Git-Insight Dashboard showing repository analysis interface](assets/dashboard.png)

### Commit Activity Over Time
![Chart showing commit frequency over the analysis period](assets/commit_activity.png)

### Coding Intensity Heatmap
![Heatmap visualization of coding activity by day and hour](assets/coding_intensity.png)
```

## Verification

After completing these tasks:
- [ ] `examples/` folder contains at least one sample PDF report
- [ ] `assets/` folder contains 2-3 screenshots
- [ ] README.md displays screenshots correctly when viewed on GitHub
- [ ] All screenshots are clear and professional-looking

## Tips

- **For better screenshots**: Use a repository with at least 50+ commits in the time range
- **Privacy**: Make sure not to include sensitive information in screenshots
- **Image size**: Keep screenshots under 1MB each for faster loading
- **Quality**: Take screenshots at standard resolution (1920x1080 recommended)
