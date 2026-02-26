import os

# Optional imports for LLMs
try:
    import openai
except ImportError:
    openai = None

try:
    from google import genai
except ImportError:
    genai = None

class LLMAnalyzer:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "GEMINI").upper()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.enabled = False
        self.gemini_client = None

        if self.provider == "OPENAI" and self.openai_key:
            if openai:
                # Basic check if it's new client or old
                # We defer client creation to usage to be safe
                self.enabled = True
            else:
                print("Warning: OpenAI provider selected but 'openai' package is not installed.")
        elif self.provider == "GEMINI" and self.gemini_key:
            if genai:
                try:
                    # Use new Client-based API
                    self.gemini_client = genai.Client(api_key=self.gemini_key)
                    self.enabled = True
                except Exception as e:
                    print(f"Warning: Failed to initialize Gemini client: {e}")
            else:
                print("Warning: Gemini provider selected but 'google.genai' package is not installed.")
        else:
            print("Warning: No valid LLM provider configured (keys missing). LLM features will be disabled.")
            
    def generate_text(self, prompt, model="gpt-4o"):
        """
        Generic wrapper for text generation.
        """
        if not self.enabled:
             return "LLM analysis disabled (missing keys or dependencies)."

        if self.provider == "OPENAI" and self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"Error with OpenAI: {e}"

        elif self.provider == "GEMINI" and self.gemini_key:
            if not self.gemini_client:
                return "Error: Gemini client not initialized."
            
            try:
                # Use new Client API with generate_content
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt
                )
                return response.text.strip()
            except AttributeError:
                # Handle API response structure issues
                return "Error: Unexpected API response structure from Gemini."
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle specific error types
                if 'rate' in error_msg or 'quota' in error_msg:
                    return "Error: API rate limit exceeded. Please try again later or check your quota."
                elif 'authentication' in error_msg or 'api key' in error_msg or 'unauthorized' in error_msg:
                    return "Error: Authentication failed. Please check your Gemini API key."
                elif 'timeout' in error_msg or 'network' in error_msg:
                    return "Error: Network timeout. Please check your internet connection and try again."
                elif 'safety' in error_msg or 'blocked' in error_msg:
                    return "Error: Content was blocked by safety filters. Try rephrasing your request."
                else:
                    return f"Error with Gemini: {e}"
        
        return "LLM not configured."

    def summarize_commits(self, commit_logs):
        """
        Summarizes a list of commit messages.
        """
        if not commit_logs:
            return "No commits to summarize."
        
        # Limit the input size to avoid token limits
        logs_text = "\n".join(commit_logs[:50]) # Taking first 50 for brevity in demo, or smart chunking 
        prompt = f'''
        You are a senior tech lead. Analyze the following commit logs and provide a professional monthly summary.
        Focus on:
        1. Main technical achievements.
        2. Key patterns or refactoring efforts.
        3. Skills demonstrated (e.g. Python, API design, etc).
        
        Commits:
        {logs_text}
        
        Summary:
        '''
        return self.generate_text(prompt)

    def analyze_skill_growth(self, commit_diffs_summary):
        """
        Analyzes the diffs (or summary of files changed) to predict skill growth.
        """
        prompt = f'''
        Based on the following summary of file changes and commit categories, identify the developer's skill growth.
        
        Data:
        {commit_diffs_summary}
        
        Output a short paragraph describing the skill growth.
        '''
        return self.generate_text(prompt)
