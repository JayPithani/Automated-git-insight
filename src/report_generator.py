from fpdf import FPDF
import datetime
import os

# Theory descriptions for each chart section
CHART_DESCRIPTIONS = {
    "Commit Activity": (
        "What is Commit Activity?",
        "Commit activity tracks how frequently code changes are pushed to a repository over time. "
        "Each point on this line chart represents the number of commits made on a given day. "
        "High peaks indicate days of intense development, while flat periods may represent "
        "weekends, holidays, or planning phases.\n\n"
        "How to read this chart:\n"
        "- X-axis: Timeline (dates)\n"
        "- Y-axis: Number of commits per day\n"
        "- Peaks = High productivity days\n"
        "- Flat lines = Low activity or rest periods\n\n"
        "Why it matters: Consistent commit activity is a sign of healthy development habits. "
        "Irregular spikes may indicate last-minute rushes before deadlines."
    ),
    "Category Distribution": (
        "What is Category Distribution?",
        "This pie chart classifies all commits into categories based on their commit messages "
        "using Conventional Commit standards and regex pattern matching.\n\n"
        "Categories explained:\n"
        "- Feature (feat:): New functionality added to the project\n"
        "- Bug Fix (fix:): Corrections to existing broken functionality\n"
        "- Refactor: Code restructuring without changing behavior\n"
        "- Documentation (docs:): Updates to README, comments, or guides\n"
        "- Other: Commits that don't follow conventional patterns\n\n"
        "Why it matters: A healthy project typically has a balance of features and fixes. "
        "Too many bug fixes may indicate technical debt, while too many features with no fixes "
        "may suggest insufficient testing."
    ),
    "Coding Intensity": (
        "What is Coding Intensity?",
        "The coding intensity heatmap reveals WHEN you are most productive during the week. "
        "It maps commit frequency across every hour of the day (0-23) and every day of the week.\n\n"
        "How to read this chart:\n"
        "- X-axis: Hour of the day (0 = midnight, 12 = noon, 23 = 11 PM)\n"
        "- Y-axis: Day of the week (Monday to Sunday)\n"
        "- Darker green = More commits at that time\n"
        "- Light/white = Low or no activity\n\n"
        "Why it matters: Understanding your peak coding hours helps you schedule deep work "
        "during your most productive times and plan meetings or reviews during low-activity periods."
    ),
    "Top Modified Files": (
        "What are Top Modified Files?",
        "This bar chart shows which files in the repository have been changed most frequently "
        "across all commits in the analyzed period.\n\n"
        "How to read this chart:\n"
        "- Y-axis: File names\n"
        "- X-axis: Number of times each file was modified\n"
        "- Longer bars = More frequently changed files\n\n"
        "Why it matters: Files that are modified very frequently are called 'hot spots'. "
        "They may indicate core business logic, files with technical debt, or areas that "
        "need refactoring or better modularization."
    ),
    "LOC Analysis": (
        "What is LOC Analysis?",
        "Lines of Code (LOC) Analysis tracks how much code was added (green) vs removed (red) "
        "each day over the analyzed period. This is a stacked bar chart showing net code changes.\n\n"
        "How to read this chart:\n"
        "- Green bars: Lines of code added\n"
        "- Red bars: Lines of code deleted\n"
        "- X-axis: Timeline\n"
        "- Y-axis: Number of lines\n\n"
        "Why it matters: A healthy codebase often shows balanced additions and deletions "
        "(refactoring). Consistently adding without deleting may indicate growing technical debt, "
        "while large deletions often signal cleanup or optimization work."
    ),
    "Feature vs Bugfix": (
        "What is Feature vs Bugfix Trend?",
        "This line chart compares two key commit types over time: new Features being built "
        "vs Bug Fixes being applied. It shows the velocity and stability balance of the project.\n\n"
        "How to read this chart:\n"
        "- Blue line: Feature commits over time\n"
        "- Orange line: Bug fix commits over time\n"
        "- X-axis: Timeline\n"
        "- Y-axis: Number of commits per day\n\n"
        "Why it matters: When bug fixes consistently outnumber features, it signals the project "
        "is in maintenance/stabilization mode. When features dominate, the project is in active "
        "development. The ideal ratio depends on the project's current phase."
    ),
}


class ReportGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Automated Git-Insight Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Encode to latin-1 safely
        safe_body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, safe_body)
        self.ln()

    def section_heading(self, title):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(30, 80, 160)
        safe_title = title.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 8, safe_title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def divider(self):
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def add_chart_with_theory(self, chart_title, image_path):
        """Add a new page with theory explanation followed by the chart image."""
        self.add_page()

        # Section header
        self.chapter_title(chart_title)

        # Get theory content
        if chart_title in CHART_DESCRIPTIONS:
            sub_heading, description = CHART_DESCRIPTIONS[chart_title]
            self.section_heading(sub_heading)
            self.chapter_body(description)
        
        self.divider()

        # Add the chart image below the theory
        if image_path and os.path.exists(image_path):
            self.set_font('Arial', 'B', 10)
            self.set_text_color(80, 80, 80)
            self.cell(0, 6, f'Chart: {chart_title}', 0, 1, 'C')
            self.set_text_color(0, 0, 0)
            self.ln(2)

            # Calculate image positioning
            page_width = 190
            self.image(image_path, x=10, w=page_width)
        else:
            self.set_font('Arial', 'I', 10)
            self.set_text_color(150, 0, 0)
            self.cell(0, 10, '[Chart image not available]', 0, 1, 'C')
            self.set_text_color(0, 0, 0)

    def generate_report(self, summary_text, skill_text, plots, output_file="report.pdf"):
        # ── Page 1: Cover + AI Summary ──
        self.add_page()

        # Date
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, f'Date: {datetime.date.today()}', 0, 1)
        self.ln(3)

        # Introduction block
        self.chapter_title('About This Report')
        self.chapter_body(
            "This report was automatically generated by the Automated Git-Insight tool. "
            "It analyzes your GitHub commit history and provides visual analytics, "
            "AI-powered summaries, and skill growth insights based on your coding patterns "
            "over the selected time period.\n\n"
            "The report is divided into the following sections:\n"
            "1. Executive Summary - AI-generated overview of your work\n"
            "2. Skill Growth Analysis - Technologies and patterns identified\n"
            "3. Commit Activity - Daily commit frequency over time\n"
            "4. Category Distribution - Breakdown of commit types\n"
            "5. Coding Intensity - Your most productive hours and days\n"
            "6. Additional analytics (files, LOC, feature vs bugfix trends)"
        )

        self.divider()

        # Executive Summary
        self.chapter_title('Executive Summary')
        self.section_heading('AI-Generated Summary of Your Work')
        self.chapter_body(summary_text)

        self.divider()

        # Skill Growth
        self.chapter_title('Skill Growth Analysis')
        self.section_heading('Technologies and Patterns Identified by AI')
        self.chapter_body(skill_text)

        # ── Pages 2+: Theory + Chart for each visualization ──
        for title, path in plots.items():
            self.add_chart_with_theory(title, path)

        self.output(output_file)
        print(f"Report generated: {output_file}")