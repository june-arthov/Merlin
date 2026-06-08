import subprocess
import json
import urllib.parse
from .base import BaseTool

class GoogleSearch(BaseTool):
    @property
    def name(self): return "google_search"
    @property
    def category(self): return "web"
    @property
    def description(self): return "Performs a Google Search."
    @property
    def parameters(self): return {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    def execute(self, query):
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        try:
            cmd = f'curl -s -A "Mozilla/5.0" "{url}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {"query": query, "url": url, "status": "Captured HTML preview."}
        except Exception as e: return {"error": str(e)}

class WebFetch(BaseTool):
    @property
    def name(self): return "web_fetch"
    @property
    def category(self): return "web"
    @property
    def description(self): return "Fetches raw content from a URL."
    @property
    def parameters(self): return {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
    def execute(self, url):
        try:
            cmd = f'curl -s -L -A "Mozilla/5.0" "{url}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout
            if len(output) > 10000: output = output[:5000] + "\n...[TRUNCATED]...\n" + output[-5000:]
            return {"content": output}
        except Exception as e: return {"error": str(e)}
