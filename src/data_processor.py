import pandas as pd
import re

class DataProcessor:
    def __init__(self, data_frame):
        self.df = data_frame

    def clean_data(self):
        """
        Removes noise from the dataframe.
        """
        if self.df.empty:
            return self.df
        
        # remove very small changes ? (Optional, maybe keep them but flag them)
        # For now, let's just ensure we have valid messages
        self.df = self.df.dropna(subset=['message'])
        
        # Filter out merge commits if desired
        # self.df = self.df[~self.df['message'].str.startswith('Merge pull request')]
        
        return self.df

    def classify_commit(self, message):
        """
        Enhanced regex-based classifier supporting Conventional Commits.
        """
        msg_lower = message.lower()
        
        # Regex patterns for Conventional Commits
        patterns = {
            'Bug Fix': r'^(fix|hotfix|patch|bug)(\(.*\))?:',
            'Feature': r'^(feat|feature|add|new)(\(.*\))?:',
            'Refactor': r'^(refactor|clean|structure|rewrite)(\(.*\))?:',
            'Documentation': r'^(docs|doc|readme)(\(.*\))?:',
            'Testing': r'^(test|tests|spec|coverage)(\(.*\))?:',
            'Chore': r'^(chore|ci|build|workflow|update|upgrade|bump)(\(.*\))?:',
            'Style': r'^(style|format|lint)(\(.*\))?:',
            'Perf': r'^(perf|optimize|performance)(\(.*\))?:'
        }

        # Check for strict prefix match (High confidence)
        for category, pattern in patterns.items():
            if re.search(pattern, msg_lower):
                return category

        # Fallback to keyword search (Lower confidence)
        if any(x in msg_lower for x in ['fix', 'bug', 'resolve', 'patch', 'issue']):
            return 'Bug Fix'
        elif any(x in msg_lower for x in ['feat', 'add', 'new', 'implement', 'create']):
            return 'Feature'
        elif any(x in msg_lower for x in ['refactor', 'clean', 'structure', 'rewrite', 'move']):
            return 'Refactor'
        elif any(x in msg_lower for x in ['docs', 'readme', 'comment', 'typo']):
            return 'Documentation'
        elif any(x in msg_lower for x in ['test', 'spec', 'coverage', 'unit']):
            return 'Testing'
        elif any(x in msg_lower for x in ['chore', 'update', 'upgrade', 'bump', 'dependency']):
            return 'Chore'
        else:
            return 'Other'

    def process(self):
        """
        Runs the cleaning and classification pipeline.
        """
        self.df = self.clean_data()
        if not self.df.empty:
            self.df['category'] = self.df['message'].apply(self.classify_commit)
            # Ensure date is datetime
            self.df['date'] = pd.to_datetime(self.df['date'])
        return self.df
