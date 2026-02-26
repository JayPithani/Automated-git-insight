import os
import time
from github import Github, GithubException, RateLimitExceededException
from datetime import datetime
import pandas as pd

class GithubConnector:
    def __init__(self, token=None):
        self.g = Github(token)
        self.token = token

    def get_repo(self, repo_name):
        """
        Connects to a specific repository.
        repo_name: "username/repo" string.
        """
        try:
            return self.g.get_repo(repo_name)
        except RateLimitExceededException:
            print("Error: GitHub API rate limit exceeded. Please try again later or provide a token.")
            return None
        except GithubException as e:
            if e.status == 404:
                print(f"Error: Repository '{repo_name}' not found. Please check the name and try again.")
            elif e.status == 401:
                print("Error: Invalid or missing GitHub token. Please check your credentials.")
            else:
                print(f"Error connecting to repo {repo_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error connecting to repo {repo_name}: {e}")
            return None

    def fetch_commits(self, repo_name, since=None, until=None):
        """
        Fetches commits from a repo within a date range.
        Returns a list of dictionaries with raw commit data.
        """
        repo = self.get_repo(repo_name)
        if not repo:
            return pd.DataFrame() # Return empty DataFrame on failure

        # Default query args
        query_args = {}
        if since:
            query_args['since'] = since
        if until:
            query_args['until'] = until

        print(f"Fetching commits for {repo_name}...")
        try:
            commits = repo.get_commits(**query_args)
            
            data = []
            # Iterate with a limit or careful error handling to avoid infinite hangs on huge repos
            # For now, we iterate normally but catch interruptions
            count = 0
            for commit in commits:
                try:
                    # Extract basic info
                    author_name = commit.commit.author.name
                    author_email = commit.commit.author.email
                    date = commit.commit.author.date
                    message = commit.commit.message
                    sha = commit.sha
                    
                    # Stats (lines added/removed) 
                    # Note: accessing commit.stats triggers an API call per commit
                    stats = commit.stats
                    additions = stats.additions
                    deletions = stats.deletions
                    
                    # Files modified
                    files = [f.filename for f in commit.files]

                    data.append({
                        'sha': sha,
                        'author': author_name,
                        'email': author_email,
                        'date': date,
                        'message': message,
                        'additions': additions,
                        'deletions': deletions,
                        'files': files
                    })
                    count += 1
                    if count % 20 == 0:
                        print(f"Fetched {count} commits...", end='\r')
                        
                except RateLimitExceededException:
                    print(f"\nRate limit exceeded while fetching commit details after {count} commits.")
                    break
                except Exception as e:
                    print(f"\nError processing commit {sha}: {e}")
                    continue
                    
            print(f"\nSuccessfully fetched {len(data)} commits.")
            return pd.DataFrame(data)

        except RateLimitExceededException:
            print("Error: GitHub API rate limit exceeded during commit listing.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if token:
        connector = GithubConnector(token)
        # Example: connector.fetch_commits("octocat/Hello-World")
    else:
        print("No GITHUB_TOKEN found.")
