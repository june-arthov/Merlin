from playwright.sync_api import sync_playwright
from .base import BaseTool
import base64
import os

class BrowserAutomation(BaseTool):
    @property
    def name(self): return "browser_automation"
    
    @property
    def category(self): return "web"
    
    @property
    def description(self): return "Automates a headless browser to extract dynamic JS content, click elements, or take screenshots."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["goto", "screenshot", "click", "extract_text"], "description": "Action to perform."},
                "url": {"type": "string", "description": "URL to navigate to (required for 'goto')."},
                "selector": {"type": "string", "description": "CSS selector for click or extract_text."},
                "timeout": {"type": "integer", "description": "Timeout in milliseconds (default 30000)."}
            },
            "required": ["action"]
        }

    def execute(self, action, url=None, selector=None, timeout=30000):
        try:
            with sync_playwright() as p:
                # We launch chromium in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(timeout)

                result = {}

                if action == "goto":
                    if not url: return {"error": "URL is required for goto."}
                    page.goto(url)
                    result["status"] = f"Successfully navigated to {url}"
                    result["title"] = page.title()
                
                elif action == "extract_text":
                    if not url: return {"error": "URL is required."}
                    page.goto(url)
                    if selector:
                        element = page.locator(selector).first
                        text = element.inner_text()
                    else:
                        text = page.locator("body").inner_text()
                    
                    # Truncate if too long
                    if len(text) > 10000:
                        text = text[:5000] + "\n...[TRUNCATED]...\n" + text[-5000:]
                    result["text"] = text

                elif action == "screenshot":
                    if not url: return {"error": "URL is required."}
                    page.goto(url)
                    os.makedirs("merlin_outputs", exist_ok=True)
                    path = f"merlin_outputs/screenshot_{int(page.evaluate('Date.now()'))}.png"
                    page.screenshot(path=path)
                    result["status"] = f"Screenshot saved to {path}"

                elif action == "click":
                    if not url or not selector: return {"error": "URL and selector are required for click."}
                    page.goto(url)
                    page.locator(selector).click()
                    page.wait_for_load_state("networkidle")
                    result["status"] = f"Clicked {selector}"
                    result["new_url"] = page.url

                browser.close()
                return result
        except Exception as e:
            return {"error": f"Browser Error: {str(e)}"}
