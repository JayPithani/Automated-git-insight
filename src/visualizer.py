import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

class Visualizer:
    def __init__(self, data_frame, output_dir="output"):
        self.df = data_frame
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Ensure we don't have open figures
        plt.close('all')

    def plot_commits_over_time(self):
        """
        Plots the number of commits per day/week.
        """
        if self.df.empty:
             return None
             
        fig = plt.figure(figsize=(10, 6))
        # Resample by day
        daily_counts = self.df.set_index('date').resample('D').size()
        sns.lineplot(data=daily_counts)
        plt.title('Commit Activity Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Commits')
        
        path = os.path.join(self.output_dir, 'commits_over_time.png')
        plt.tight_layout()
        plt.savefig(path)
        # We don't close here, we let the caller handle or it stays in memory (minor leak if loop, but okay for this CLI/App)
        # Actually for CLI we should close.
        # Let's return both path and fig, and let caller decide.
        # But to avoid breaking main.py which expects just path string, I'll store fig in self for app usage? 
        # No, that's messier.
        # I'll just change the return to be 'path' and assume the app will re-read the image or uses a new method?
        # Re-reading image is safe and easy for Streamlit. `st.image(path)` works great.
        # So I will NOT change the return type. I will just ensure the image is saved correctly and high quality.
        # PROPOSAL: Stick to saving images. Streamlit can display images.
        # This requires NO changes to Visualizer return signatures. PERFECT.
        # I will just ensure plt.close() is called to free memory.
        plt.close(fig)
        return path

    def plot_category_distribution(self):
        """
        Plots a pie chart of commit categories.
        """
        if self.df.empty or 'category' not in self.df.columns:
            return None
            
        fig = plt.figure(figsize=(8, 8))
        counts = self.df['category'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Commit Categories')
        
        path = os.path.join(self.output_dir, 'category_distribution.png')
        plt.tight_layout()
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_top_files(self):
        """
        Plots the most frequently modified files.
        """
        if self.df.empty: 
            return None
            
        # Explode the files list
        all_files = []
        for files in self.df['files']:
            if isinstance(files, list):
                all_files.extend(files)
        
        if not all_files:
            return None
            
        file_counts = pd.Series(all_files).value_counts().head(10)
        
        fig = plt.figure(figsize=(10, 6))
        sns.barplot(x=file_counts.values, y=file_counts.index, orient='h')
        plt.title('Most Modified Files')
        plt.xlabel('Count')
        
        path = os.path.join(self.output_dir, 'top_files.png')
        plt.tight_layout()
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_coding_intensity(self):
        """
        Heatmap of Hour of Day vs Day of Week.
        """
        if self.df.empty:
            return None

        # Extract hour and day of week
        self.df['hour'] = self.df['date'].dt.hour
        self.df['day_name'] = self.df['date'].dt.day_name()
        
        # Order days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Pivot table
        heatmap_data = self.df.pivot_table(index='day_name', columns='hour', aggfunc='size', fill_value=0)
        # Reindex to ensure all days are present
        heatmap_data = heatmap_data.reindex(days_order)
        
        fig = plt.figure(figsize=(12, 6))
        sns.heatmap(heatmap_data, cmap="Greens", linewidths=.5)
        plt.title('Coding Intensity (Commits by Day/Hour)')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        
        path = os.path.join(self.output_dir, 'coding_intensity.png')
        plt.tight_layout()
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_loc_analysis(self):
        """
        Stacked bar chart of Additions vs Deletions over time.
        """
        if self.df.empty:
            return None

        fig = plt.figure(figsize=(12, 6))
        daily_stats = self.df.set_index('date').resample('D')[['additions', 'deletions']].sum()
        
        # Use simple bar chart with bottom parameter for stacking? Or simple plot
        # Actually seaborn doesn't do stacked bars easily, let's use pandas plot
        # To make it work with explicit figure, we pass ax
        ax = plt.gca()
        daily_stats.plot(kind='bar', stacked=True, color=['green', 'red'], width=1.0, ax=ax)
        
        plt.title('Lines of Code Added vs Removed')
        plt.xlabel('Date')
        plt.ylabel('Lines of Code')
        # Reduce x-axis ticks clutter: simple method
        plt.locator_params(axis='x', nbins=10) 
        
        path = os.path.join(self.output_dir, 'loc_analysis.png')
        plt.tight_layout()
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_feature_vs_bugfix(self):
        """
        Line chart comparing Feature and Bug Fix trends.
        """
        if self.df.empty or 'category' not in self.df.columns:
            return None

        # Filter only Feature and Bug Fix
        mask = self.df['category'].isin(['Feature', 'Bug Fix'])
        filtered_df = self.df[mask]
        
        if filtered_df.empty:
            return None

        fig = plt.figure(figsize=(10, 6))
        # Pivot by category over time
        pivot_data = filtered_df.set_index('date').groupby([pd.Grouper(freq='D'), 'category']).size().unstack(fill_value=0)
        
        sns.lineplot(data=pivot_data)
        plt.title('Feature vs Bug Fixes Over Time')
        plt.xlabel('Date')
        plt.ylabel('Count')
        
        path = os.path.join(self.output_dir, 'feature_vs_bugfix.png')
        plt.tight_layout()
        plt.savefig(path)
        plt.close(fig)
        return path
