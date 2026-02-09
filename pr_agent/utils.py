"""Utility functions for PR Agent"""

def generate_character_prompt(character_name: str, work_name: str, quote_context: str = "") -> str:
    """Generate prompt for character description generation.
    
    Args:
        character_name: Name of the character
        work_name: Name of the work/series
        quote_context: Optional context from web search
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""あなたは「{character_name}」（作品名: {work_name}）というキャラクターの専門家です。
このキャラクターの**口癖、決め台詞、特徴的な語尾、口調**を中心に、性格や特徴を200文字程度で簡潔に説明してください。

重要: 以下の要素を必ず含めてください:
- 頻繁に使う口癖（例: 「〇〇だぜ」「〜なのだ」など）
- 有名な決め台詞や名言
- 特徴的な語尾や話し方のパターン
- 一人称（僕、俺、私など）
- 口調の特徴（丁寧語、タメ口、方言など）

PRメッセージ生成時にこのキャラクターになりきるための情報として使用します。
口調を再現できる具体的な情報を優先してください。

{quote_context}

出力形式: 説明文のみを出力してください。見出しや前置きは不要です。"""
    
    return prompt
