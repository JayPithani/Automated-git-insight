from fpdf import FPDF
import datetime
import os

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
        self.multi_cell(0, 5, body)
        self.ln()

    def add_plot(self, image_path, title):
        if image_path and os.path.exists(image_path):
            self.add_page()
            self.chapter_title(title)
            self.image(image_path, x=10, w=190)

    def generate_report(self, summary_text, skill_text, plots, output_file="report.pdf"):
        self.add_page()
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'Date: {datetime.date.today()}', 0, 1)
        self.ln(5)

        self.chapter_title('Executive Summary')
        self.chapter_body(summary_text)

        self.chapter_title('Skill Growth Analysis')
        self.chapter_body(skill_text)

        # Add visual analytics
        for title, path in plots.items():
            if path:
                self.add_plot(path, title)

        self.output(output_file)
        print(f"Report generated: {output_file}")
