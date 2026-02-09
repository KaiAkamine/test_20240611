import urllib.request
import urllib.error
import json
from typing import Optional

class OllamaClient:
    def __init__(self, api_url: str = "http://localhost:11434/api/generate", model: str = "llama3"):
        self.api_url = api_url
        self.model = model

    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        """Generates text using the Ollama API."""
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.api_url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                text = result.get("response", "")
                # Sanitize output: Replace full-width space (which may render as <0xE3><0x80><0x80>) with normal space
                return text.replace("\u3000", " ")
        except urllib.error.URLError as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}\nMake sure Ollama is running (e.g., 'ollama serve')")

    def check_connection(self) -> bool:
        """Checks if Ollama is running."""
        try:
            # Check the root URL (usually http://localhost:11434/)
            root_url = self.api_url.replace("/api/generate", "")
            with urllib.request.urlopen(root_url, timeout=2) as response:
                return response.status == 200
        except:
            return False
