import urllib.request
import urllib.error
import json
from typing import Optional, List, Dict

class OllamaClient:
    def __init__(self, api_url: str = "http://localhost:11434/api/generate", model: str = "llama3"):
        self.api_url = api_url
        self.model = model
        self.base_url = api_url.replace("/api/generate", "")

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
                return self._sanitize_text(text)
        except urllib.error.URLError as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}\nMake sure Ollama is running (e.g., 'ollama serve')")
    
    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Remove hex byte representations and normalize special characters."""
        import re
        # Remove hex byte patterns like <0xE3><0x80><0x80>
        text = re.sub(r'<0x[0-9A-Fa-f]{2}>', '', text)
        # Replace full-width space with normal space
        text = text.replace('\u3000', ' ')
        return text

    def check_connection(self) -> bool:
        """Checks if Ollama is running."""
        try:
            with urllib.request.urlopen(self.base_url, timeout=2) as response:
                return response.status == 200
        except:
            return False
    
    def list_local_models(self) -> List[Dict[str, str]]:
        """Lists locally installed models."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("models", [])
        except Exception as e:
            raise Exception(f"Failed to list models: {str(e)}")
    
    def pull_model(self, model_name: str, progress_callback=None):
        """Downloads a model from Ollama library with streaming progress."""
        try:
            payload = {"name": model_name, "stream": True}
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(f"{self.base_url}/api/pull", data=data, headers={"Content-Type": "application/json"})
            
            with urllib.request.urlopen(req, timeout=600) as response:
                for line in response:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if progress_callback:
                                progress_callback(chunk)
                            if chunk.get("status") == "success":
                                return True
                        except json.JSONDecodeError:
                            continue
            return True
        except Exception as e:
            raise Exception(f"Failed to pull model: {str(e)}")
    
    def unload_model(self, model_name: str) -> bool:
        """Unloads a model from memory."""
        try:
            payload = {"model": model_name, "keep_alive": 0}
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(f"{self.base_url}/api/generate", data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                return True
        except:
            return False
    
    @staticmethod
    def get_popular_models() -> List[Dict[str, str]]:
        """Returns a list of popular Ollama models with metadata."""
        return [
            # 汎用モデル
            {"name": "llama3.2", "params": "3B", "size": "2GB", "desc": "🔥 最新の小型高性能モデル"},
            {"name": "llama3.2:1b", "params": "1B", "size": "1.3GB", "desc": "⚡ 超軽量版"},
            {"name": "llama3.1", "params": "8B", "size": "4.7GB", "desc": "🚀 高性能汎用モデル"},
            {"name": "llama3.1:70b", "params": "70B", "size": "40GB", "desc": "💪 最高性能（要大容量）"},
            {"name": "llama3", "params": "8B", "size": "4.7GB", "desc": "✅ 安定版汎用モデル"},
            {"name": "gemma2", "params": "9B", "size": "5.4GB", "desc": "🔵 Google製高性能"},
            {"name": "gemma2:2b", "params": "2B", "size": "1.6GB", "desc": "🔵 Google製軽量版"},
            {"name": "gemma2:27b", "params": "27B", "size": "16GB", "desc": "🔵 Google製大型"},
            {"name": "mistral", "params": "7B", "size": "4.1GB", "desc": "⚡ 高速で高品質"},
            {"name": "mixtral:8x7b", "params": "47B", "size": "26GB", "desc": "🎯 MoE高性能モデル"},
            {"name": "phi3", "params": "3.8B", "size": "2.3GB", "desc": "🟣 Microsoft製小型"},
            {"name": "phi3:14b", "params": "14B", "size": "7.9GB", "desc": "🟣 Microsoft製中型"},
            {"name": "qwen2.5", "params": "7B", "size": "4.7GB", "desc": "🌏 多言語対応"},
            {"name": "qwen2.5:14b", "params": "14B", "size": "9GB", "desc": "🌏 多言語大型"},
            {"name": "qwen2.5:32b", "params": "32B", "size": "19GB", "desc": "🌏 多言語最大"},
            # コード特化
            {"name": "codellama", "params": "7B", "size": "3.8GB", "desc": "💻 コード生成特化"},
            {"name": "codellama:13b", "params": "13B", "size": "7.4GB", "desc": "💻 コード生成中型"},
            {"name": "codellama:34b", "params": "34B", "size": "19GB", "desc": "💻 コード生成大型"},
            {"name": "deepseek-coder", "params": "6.7B", "size": "3.8GB", "desc": "💻 コード特化高性能"},
            {"name": "deepseek-coder:33b", "params": "33B", "size": "19GB", "desc": "💻 コード特化大型"},
            {"name": "codegemma", "params": "7B", "size": "5GB", "desc": "💻 Google製コード"},
            # 日本語強化
            {"name": "llama3-elyza-jp-8b", "params": "8B", "size": "4.9GB", "desc": "🇯🇵 日本語特化"},
            {"name": "command-r", "params": "35B", "size": "20GB", "desc": "🌐 多言語RAG対応"},
            # 軽量・高速
            {"name": "tinyllama", "params": "1.1B", "size": "637MB", "desc": "⚡ 超軽量高速"},
            {"name": "orca-mini", "params": "3B", "size": "1.9GB", "desc": "⚡ 軽量汎用"},
            {"name": "stablelm2", "params": "1.6B", "size": "1.1GB", "desc": "⚡ 軽量安定"},
        ]
