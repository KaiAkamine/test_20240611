import urllib.request
import json

def check_ollama():
    url = "http://localhost:11434/api/tags"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("Ollama is running!")
                print("Available models:")
                for model in data.get('models', []):
                    print(f" - {model['name']}")
            else:
                print(f"Ollama returned status: {response.status}")
    except Exception as e:
        print(f"Failed to connect to Ollama: {e}")

if __name__ == "__main__":
    check_ollama()
