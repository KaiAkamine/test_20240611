#!/bin/bash
# Streamlit起動スクリプト

echo "🚀 PR Message Generator を起動しています..."
echo ""
echo "ブラウザが自動的に開かない場合は、以下のURLにアクセスしてください:"
echo "http://localhost:8501"
echo ""

# 仮想環境を有効化してStreamlitを起動
source venv/bin/activate
streamlit run pr_agent/app.py
