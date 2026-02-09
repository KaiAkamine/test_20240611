import streamlit as st
import json
import os
import sys

# Adjust path to allow imports if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pr_agent.client import OllamaClient
from pr_agent.prompts import get_messages
from pr_agent.search import get_random_quote_context

# Page Config
st.set_page_config(page_title="PR Message Generator", page_icon="🚀", layout="wide")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("config.json が見つかりません。")
        return None
    except Exception as e:
        st.error(f"設定の読み込みに失敗しました: {e}")
        return None

def save_config(new_config):
    try:
        with open(CONFIG_PATH, "w", encoding='utf-8') as f:
            json.dump(new_config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"設定の保存に失敗しました: {e}")
        return False

def main():
    config = load_config()
    if not config:
        return

    # Get characters list
    characters = config.get("characters", [])
    if not characters:
        st.error("キャラクターが登録されていません。")
        return
    
    active_index = config.get("active_character_index", 0)
    if active_index >= len(characters):
        active_index = 0
        config["active_character_index"] = 0
    
    character_config = characters[active_index]
    char_name = character_config.get("name", "未設定")
    work_name = character_config.get("work", "未設定")
    
    # Sidebar: Character Selection
    st.sidebar.header("キャラクター選択 🎭")
    character_names = [c.get("name", f"Character {i}") for i, c in enumerate(characters)]
    
    selected_name = st.sidebar.selectbox(
        "担当キャラクター",
        character_names,
        index=active_index,
        key="character_selector"
    )
    
    # Update active character if changed
    new_index = character_names.index(selected_name)
    if new_index != active_index:
        config["active_character_index"] = new_index
        if save_config(config):
            st.rerun()
    
    # Use the selected character (either active_index or new_index, they should be the same at this point)
    active_index = new_index
    character_config = characters[active_index]
    char_name = character_config.get("name", "未設定")
    work_name = character_config.get("work", "未設定")




    
    # Sidebar: Info
    st.sidebar.markdown("---")
    st.sidebar.header("現在の担当 👤")
    st.sidebar.info(f"**名前:** {char_name}\n\n**作品:** {work_name}")
    
    # Sidebar: Settings Editor
    with st.sidebar.expander("設定エディタ ⚙️"):
        st.markdown("### 現在のキャラクター編集")
        with st.form("edit_character_form"):
            new_name = st.text_input("名前", value=char_name)
            new_work = st.text_input("作品名", value=work_name)
            new_desc = st.text_area("詳細・口調", value=character_config.get("description", ""), height=100)
            
            submitted = st.form_submit_button("更新 💾")
            if submitted:
                characters[active_index]["name"] = new_name
                characters[active_index]["work"] = new_work
                characters[active_index]["description"] = new_desc
                config["characters"] = characters
                
                if save_config(config):
                    st.success("更新しました！")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### キャラクター管理")
        
        # Add new character
        st.markdown("**新規キャラクター追加**")
        
        # Initialize session state
        if "temp_char_name" not in st.session_state:
            st.session_state.temp_char_name = ""
        if "temp_char_work" not in st.session_state:
            st.session_state.temp_char_work = ""
        if "temp_char_desc" not in st.session_state:
            st.session_state.temp_char_desc = ""
        
        # Character form
        with st.form("add_character_form", clear_on_submit=False):
            add_char_name = st.text_input("名前", value=st.session_state.temp_char_name)
            add_char_work = st.text_input("作品名", value=st.session_state.temp_char_work)
            add_char_desc = st.text_area("詳細・口調", value=st.session_state.temp_char_desc, height=120)
            
            col1, col2 = st.columns(2)
            with col1:
                generate_btn = st.form_submit_button("詳細を自動生成 🤖", type="secondary")
            with col2:
                add_btn = st.form_submit_button("追加 ➕", type="primary")
            
            if generate_btn:
                if add_char_name and add_char_work:
                    with st.spinner(f"{add_char_name} の詳細を生成中..."):
                        try:
                            client = OllamaClient(api_url=config["api_url"], model=config["model"])
                            prompt = f"""あなたは「{add_char_name}」（作品名: {add_char_work}）というキャラクターの専門家です。
このキャラクターの性格、口調、決め台詞、特徴を200文字程度で簡潔に説明してください。
PRメッセージ生成時にこのキャラクターになりきるための情報として使用します。

出力形式: 説明文のみを出力してください。見出しや前置きは不要です。"""
                            
                            generated = client.generate_text(prompt)
                            st.session_state.temp_char_name = add_char_name
                            st.session_state.temp_char_work = add_char_work
                            st.session_state.temp_char_desc = generated
                            st.success("生成完了！フォームが更新されました。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"生成に失敗しました: {e}")
                else:
                    st.warning("名前と作品名を入力してください。")
            
            if add_btn:
                if add_char_name:
                    new_character = {
                        "name": add_char_name,
                        "work": add_char_work,
                        "description": add_char_desc
                    }
                    characters.append(new_character)
                    config["characters"] = characters
                    config["active_character_index"] = len(characters) - 1
                    
                    # Clear temp state
                    st.session_state.temp_char_name = ""
                    st.session_state.temp_char_work = ""
                    st.session_state.temp_char_desc = ""
                    
                    if save_config(config):
                        st.success(f"{add_char_name} を追加しました！")
                        st.rerun()
                else:
                    st.warning("名前を入力してください。")






        
        # Delete character
        if len(characters) > 1:
            if st.button("現在のキャラクターを削除 🗑️", type="secondary"):
                characters.pop(active_index)
                config["characters"] = characters
                config["active_character_index"] = 0
                
                if save_config(config):
                    st.success("削除しました！")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 生成設定")
        with st.form("generation_settings_form"):
            new_use_search = st.checkbox("インターネット検索を使用する", value=config.get("use_search", False))
            new_target_length = st.number_input("目安文字数", value=config.get("target_length", 300), step=50, min_value=50)
            
            gen_submitted = st.form_submit_button("保存 💾")
            if gen_submitted:
                config["use_search"] = new_use_search
                config["target_length"] = new_target_length
                
                if save_config(config):
                    st.success("保存しました！")
                    st.rerun()

    # Main Area
    st.title(f"PR Message Generator: {char_name} 🚀")
    
    st.markdown(f"""
    **{char_name}** があなたのPRメッセージを代筆します。
    変更内容を入力してください！
    """)

    input_text = st.text_area("変更内容 (Diff または 要約)", height=200, placeholder="ここに git diff の結果や、変更内容の要約を貼り付けてください...")

    col1, col2 = st.columns(2)
    
    generate_pr = col1.button("PRメッセージを生成 ✨", type="primary", use_container_width=True)
    generate_merge = col2.button("マージメッセージを生成 🔀", use_container_width=True)

    if generate_pr or generate_merge:
        message_type = "pr" if generate_pr else "merge"
        
        client = OllamaClient(api_url=config["api_url"], model=config["model"])
        
        # Check connection
        if not client.check_connection():
            st.error(f"Ollama ({config['api_url']}) に接続できませんでした。Ollamaが起動しているか確認してください。")
            return

        with st.spinner(f"{char_name} がメッセージを考えています..."):
            try:
                # Search Context (if enabled)
                search_context = ""
                if config.get("use_search", False) and char_name:
                    with st.status(f"{char_name} の名言を検索中...", expanded=False) as status:
                        try:
                            search_context = get_random_quote_context(char_name, work_name)
                            status.update(label="検索完了！", state="complete")
                        except Exception as e:
                            status.update(label="検索失敗 (名言なしで続行します)", state="error")
                            st.write(f"エラー詳細: {e}")

                # Context injection based on message type
                if input_text:
                    if message_type == "merge":
                        context_prefix = "【指示: あなたはこのコードの実装者です。無事にマージが完了したことをチームに報告するメッセージを作成してください。「マージしたぞ！」というスタンスで、短潔に。】\n"
                    else:
                        context_prefix = "【指示: あなたはこのPRの作成者（実装者）です。チームメンバーに対して、このPRのレビューをお願いするメッセージを作成してください。「詳細な変更内容は記述しませんが、私のコードを見てくれ！」というスタンスで。レビューを依頼する立場であることを忘れないでください。】\n"
                    full_input = context_prefix + input_text
                else:
                    # Empty input case: Generic message
                    if message_type == "merge":
                        full_input = "【指示: あなたはこのコードの実装者です。無事にマージが完了したことをチームに報告するメッセージを作成してください。「マージしたぞ！」というスタンスで、短潔に。】"
                    else:
                        full_input = "【指示: あなたはこのPRの作成者（実装者）です。チームメンバーに対して、このPRのレビューをお願いするメッセージを作成してください。「詳細な変更内容は記述しませんが、私のコードを見てくれ！」というスタンスで。レビューを依頼する立場であることを忘れないでください。】"

                # Generate Prompt
                target_length = config.get("target_length", 300)
                prompt = get_messages(character_config, full_input, search_context, target_length=target_length)
                
                # Call LLM
                response = client.generate_text(prompt)
                
                st.success("生成完了！")
                st.markdown("### 生成結果")
                st.code(response, language=None)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
