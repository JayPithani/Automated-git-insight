import os
import time
from github import Github, GithubException, RateLimitExceededException
from datetime import datetime
import pandas as pd

class GithubConnector:
    def __init__(self, token=None):
        self.token = token
        self.g = Github(token) if token else Github()
        self._validate_token()

    def _validate_token(self):
        """
        Validates the GitHub token on startup and warns if invalid/missing.
        """
        if not self.token:
            print("Warning: No GitHub token provided. Running unauthenticated (60 req/hr limit).")
            return
        try:
            # This triggers an API call to verify the token
            user = self.g.get_user()
            _ = user.login  # force evaluation
            print(f"GitHub token validated. Authenticated as: {user.login}")
        except GithubException as e:
            if e.status == 401:
                print("ERROR: GitHub token is INVALID or EXPIRED. Falling back to unauthenticated mode.")
                print("Fix: Generate a new token at https://github.com/settings/tokens")
                self.g = Github()  # fallback to unauthenticated
                self.token = None
            else:
                print(f"Warning: Token validation failed: {e}")

    def get_repo(self, repo_name):
        """
        Connects to a specific repository.
        repo_name: "username/repo" string.
        """
        try:
            return self.g.get_repo(repo_name)
        except RateLimitExceededException:
            print("Error: GitHub API rate limit exceeded. Please try again later or provide a valid token.")
            return None
        except GithubException as e:
            if e.status == 404:
                print(f"Error: Repository '{repo_name}' not found.")
            elif e.status == 401:
                print("Error: Invalid or expired GitHub token.")
            else:
                print(f"Error connecting to repo {repo_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error connecting to repo {repo_name}: {e}")
            return None

    def fetch_commits(self, repo_name, since=None, until=None):
        """
        Fetches commits from a repo within a date range.
        Returns a DataFrame with raw commit data.
        """
        repo = self.get_repo(repo_name)
        if not repo:
            return pd.DataFrame()

        query_args = {}
        if since:
            query_args['since'] = since
        if until:
            query_args['until'] = until

        print(f"Fetching commits for {repo_name}...")
        try:
            commits = repo.get_commits(**query_args)

            data = []
            count = 0
            for commit in commits:
                try:
                    author_name = commit.commit.author.name
                    author_email = commit.commit.author.email
                    date = commit.commit.author.date
                    message = commit.commit.message
                    sha = commit.sha

                    stats = commit.stats
                    additions = stats.additions
                    deletions = stats.deletions

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
                    print(f"\nRate limit exceeded after {count} commits.")
                    break
                except Exception as e:
                    print(f"\nError processing commit: {e}")
                    continue

            print(f"\nSuccessfully fetched {len(data)} commits.")
            return pd.DataFrame(data)

        except RateLimitExceededException:
            print("Error: GitHub API rate limit exceeded during commit listing.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return pd.DataFrame()

    def get_user_repositories(self, username):
        """
        Fetches all public repositories for a GitHub user.
        Returns a list of 'username/repo' strings.
        """
        try:
            user = self.g.get_user(username)
            repos = []
            for repo in user.get_repos():
                if not repo.private:  # only public repos
                    repos.append(repo.full_name)
            print(f"Found {len(repos)} public repositories for user '{username}'.")
            return repos

        except RateLimitExceededException:
            print("Error: GitHub API rate limit exceeded while fetching repositories.")
            print("Fix: Add a valid GITHUB_TOKEN to your .env file.")
            return []
        except GithubException as e:
            if e.status == 404:
                print(f"Error: GitHub user '{username}' not found.")
                print("Check the username spelling or GitHub profile visibility.")
            elif e.status == 401:
                print("Error: GitHub token is invalid or expired.")
                print("Fix: Generate a new token at https://github.com/settings/tokens")
            elif e.status == 403:
                print("Error: API rate limit hit (403 Forbidden).")
                print("Fix: Add a valid GITHUB_TOKEN to your .env file.")
            else:
                print(f"GitHub API error ({e.status}) fetching repos for '{username}': {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching repositories for '{username}': {e}")
            return []


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    connector = GithubConnector(token)
    repos = connector.get_user_repositories("JayPithani")
    print(repos)