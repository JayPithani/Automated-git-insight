import os
import argparse
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

from src.github_connector import GithubConnector
from src.data_processor import DataProcessor
from src.llm_analyzer import LLMAnalyzer
from src.visualizer import Visualizer
from src.report_generator import ReportGenerator

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Automated Git-Insight Generator")
    parser.add_argument("--repo", type=str, required=True, help="GitHub repository name (e.g., username/repo)")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    parser.add_argument("--output", type=str, default="report.pdf", help="Output PDF filename")
    
    args = parser.parse_args()
    
    # 1. Setup
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Warning: GITHUB_TOKEN not found. Running in unauthenticated mode (rate limits apply).")
        print("To fix this, create a .env file with GITHUB_TOKEN=your_token")
    
    connector = GithubConnector(token)
    
    # 2. Fetch Data
    sys.setrecursionlimit(2000) # Safety for deep recursions if any libraries use it
    since_date = datetime.now() - timedelta(days=args.days)
    df = connector.fetch_commits(args.repo, since=since_date)
    
    if df.empty:
        print("No commits found in the specified period or failed to fetch data.")
        return

    # 3. Process Data
    processor = DataProcessor(df)
    clean_df = processor.process()
    
    if clean_df.empty:
         print("No valid commits to analyze after cleaning.")
         return
    
    # 4. LLM Analysis
    llm = LLMAnalyzer()
    print("Generating AI summary...")
    try:
        summary = llm.summarize_commits(clean_df['message'].tolist())
    except Exception as e:
        print(f"LLM Summary generation failed: {e}")
        summary = "Summary generation unavailable."
    
    # Mocking a diff summary for skill growth roughly based on categories
    categories = clean_df['category'].value_counts().to_string()
    print("Generating Skill Growth analysis...")
    try:
        skill_growth = llm.analyze_skill_growth(f"Commit Categories Distribution:\n{categories}")
    except Exception as e:
        print(f"Skill Growth analysis failed: {e}")
        skill_growth = "Skill growth analysis unavailable."

    # 5. Visualization
    print("Generating charts...")
    viz = Visualizer(clean_df)
    
    # Generate all plots (some might be None if data is missing)
    plots = {
        "Commit Activity": viz.plot_commits_over_time(),
        "Category Distribution": viz.plot_category_distribution(),
        "Top Modified Files": viz.plot_top_files(),
        "Coding Intensity": viz.plot_coding_intensity(),
        "LOC Analysis": viz.plot_loc_analysis(),
        "Feature vs Bugfix": viz.plot_feature_vs_bugfix()
    }
    
    # Remove None values
    plots = {k: v for k, v in plots.items() if v is not None}
    
    # 6. Generate Report
    print("Compiling PDF report...")
    try:
        report = ReportGenerator()
        report.generate_report(summary, skill_growth, plots, output_file=args.output)
        print(f"Done! Report saved to {args.output}")
    except Exception as e:
        print(f"Failed to generate PDF report: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
