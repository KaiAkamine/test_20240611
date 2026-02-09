# PR Message Generator

A tool to generate humorous PR and merge messages using a local LLM (Ollama).

## Requirements
- Python 3.x
- Ollama (running locally)
- `duckduckgo_search` (for fetching quotes)

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

## Usage

### CLI
Generate a PR message:
```bash
python pr_agent/main.py pr --input "Refactored login logic" --style anime
```

Generate a Merge message:
```bash
python pr_agent/main.py merge --input "Merged feature/login" --style movie
```

Options:
- `--style`: anime, movie, manga, random
- `--character`: Specific character name (e.g. "Rengoku")
- `--work`: Specific work name (e.g. "Demon Slayer")

### Web UI
Launch the web interface:
```bash
streamlit run pr_agent/app.py
```
This will open a new tab in your default browser.
1. Configure settings in the sidebar.
2. Enter your changes in the text area.
3. Click "Generate Message".
