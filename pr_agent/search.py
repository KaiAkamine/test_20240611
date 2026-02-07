from duckduckgo_search import DDGS
from typing import List
import random

def search_quotes(character: str, work: str = "") -> List[str]:
    """
    Search for quotes by a specific character or from a specific work.
    """
    query = f"{character} {work} 名言 セリフ" if work else f"{character} 名言 セリフ"
    quotes = []
    
    print(f"Searching quotes for: {query}...")
    
    try:
        results = DDGS().text(query, max_results=10)
        for result in results:
            # Simple heuristic: extract snippets that look like quotes or contain the character name
            snippet = result.get('body', '')
            if snippet:
                quotes.append(snippet)
    except Exception as e:
        print(f"Search failed: {e}")
        return []

    return quotes

def get_random_quote_context(character: str, work: str = "") -> str:
    quotes = search_quotes(character, work)
    if not quotes:
        return ""
    
    # Return a formatted string with a few random quotes to give context to the LLM
    selected_quotes = random.sample(quotes, min(3, len(quotes)))
    context = "\n".join([f"- {q}" for q in selected_quotes])
    return f"【参考: {character}の実際のセリフ/検索結果】\n{context}\n"
