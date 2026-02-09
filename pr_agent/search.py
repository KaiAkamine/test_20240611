from ddgs import DDGS
from typing import List, Tuple
import random
import requests
from bs4 import BeautifulSoup
import re
from pr_agent.client import OllamaClient

def extract_quotes_with_llm(text: str, character: str, client: OllamaClient) -> List[str]:
    """Use LLM to extract actual character quotes from text."""
    prompt = f"""あなたはテキストから実際のセリフ（発言）だけを抽出する専門家です。

【タスク】
以下のテキストから「{character}」が実際に発言したセリフのみを抽出してください。

【抽出ルール】
✓ 抽出対象：「」で囲まれたキャラクターの実際の発言のみ
✗ 除外対象：
  - 説明文（「〜というセリフ」「〜と言った」など）
  - まとめ文（「これらのセリフは〜」「以下が〜」など）
  - タイトル・見出し
  - ランキング情報
  - あらすじ・要約
  - メタ情報（「実際のセリフではなく〜」など）

【出力形式】
- セリフのみを1行に1つずつ出力
- 必ず「」付きで出力
- 余計な説明は一切不要
- 最大10個まで
- セリフが見つからない場合は何も出力しない

【例】
良い例：
「見ろ！人がゴミのようだ！」
「３分間待ってやる」

悪い例：
「見ろ！人がゴミのようだ！」というセリフが有名です
これらのセリフは印象的です

【テキスト】
{text[:3000]}

【抽出結果】"""
    
    try:
        response = client.generate_text(prompt)
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        # Filter: must start with 「 and end with 」, no meta text
        quotes = []
        exclude_keywords = [
            'セリフ', 'というセリフ', 'と言', 'これら', '以下', 'あらすじ', '要約', '描写', 
            '情報', 'ランキング', '有名', '印象', '支持', '実際のセリフではなく',
            'という', 'ところもある', 'シーンが', 'によって', 'という動機', 'が描かれ',
            '性格は', '幼少期', '戦場で', '面倒見', '意外に', 'なったのは'
        ]
        
        for line in lines:
            if line.startswith('「') and line.endswith('」'):
                # Check if it's not meta text (must not contain any exclude keywords)
                if not any(kw in line for kw in exclude_keywords):
                    # Additional check: should be relatively short (actual dialogue)
                    if len(line) < 150:
                        quotes.append(line)
        
        return quotes[:10]
    except Exception as e:
        print(f"[DEBUG] LLM extraction failed: {e}")
        return []

def extract_quotes_from_page(url: str, character: str, client: OllamaClient) -> List[str]:
    """Extract actual quotes from a webpage using LLM."""
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)
        
        # Use LLM to extract quotes
        return extract_quotes_with_llm(text[:3000], character, client)
    except Exception as e:
        print(f"[DEBUG] Failed to extract from {url}: {e}")
        return []

def search_quotes(character: str, work: str = "", client: OllamaClient = None) -> List[str]:
    """
    Search for quotes by a specific character or from a specific work.
    """
    if client is None:
        # Import config to get client settings
        import json
        import os
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        client = OllamaClient(api_url=config["api_url"], model=config["model"])
    
    query = f"{character} {work} セリフ" if work else f"{character} セリフ"
    quotes = []
    
    print(f"[DEBUG] Searching quotes for: {query}...")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region='jp-jp', max_results=5))
            print(f"[DEBUG] Got {len(results)} search results")
            
            for i, result in enumerate(results):
                url = result.get('href', '')
                title = result.get('title', '')
                print(f"[DEBUG] Fetching content from: {title}")
                
                page_quotes = extract_quotes_from_page(url, character, client)
                if page_quotes:
                    print(f"[DEBUG] Extracted {len(page_quotes)} quotes from page {i+1}")
                    for q in page_quotes:
                        print(f"[DEBUG]     - {q[:80]}..." if len(q) > 80 else f"[DEBUG]     - {q}")
                    quotes.extend(page_quotes)
                else:
                    print(f"[DEBUG] No quotes extracted from page {i+1}")
                
                # Early exit if we have enough quotes
                if len(quotes) >= 10:
                    print(f"[DEBUG] Collected enough quotes ({len(quotes)}), stopping search")
                    break
        
        print(f"[DEBUG] Total quotes collected: {len(quotes)}")
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        print(traceback.format_exc())
        return []

    return quotes

def get_random_quote_context(character: str, work: str = "") -> Tuple[str, List[str]]:
    """Returns (context_string, selected_quotes_list)"""
    quotes = search_quotes(character, work)
    if not quotes:
        return "", []
    
    # Remove duplicates while preserving order
    unique_quotes = []
    seen = set()
    for quote in quotes:
        if quote not in seen:
            unique_quotes.append(quote)
            seen.add(quote)
    
    print(f"[DEBUG] Unique quotes after deduplication: {len(unique_quotes)} (from {len(quotes)} total)")
    
    # Return a formatted string with a few random quotes to give context to the LLM
    selected_quotes = random.sample(unique_quotes, min(5, len(unique_quotes)))
    
    print(f"[DEBUG] Selected {len(selected_quotes)} quotes for LLM:")
    for i, quote in enumerate(selected_quotes, 1):
        print(f"[DEBUG]   {i}. {quote[:100]}..." if len(quote) > 100 else f"[DEBUG]   {i}. {quote}")
    
    context = "\n".join([f"- {q}" for q in selected_quotes])
    context_str = f"【参考: {character}の実際のセリフ/検索結果】\n{context}\n"
    
    return context_str, selected_quotes
