# PR Message Generator

ローカルLLM（Ollama）を使用して、キャラクターになりきったPR・マージメッセージを生成するツールです。

## 必要要件
- Python 3.x
- Ollama（ローカルで実行）
- 依存パッケージ（requirements.txt参照）

## インストール
1. リポジトリをクローン：
   ```bash
   git clone <repository-url>
   cd test_20240611
   ```

2. 依存関係をインストール：
   ```bash
   pip install -r requirements.txt
   ```

3. 初期設定：
   ```bash
   ./setup.sh
   ```
   または手動で：
   ```bash
   cp pr_agent/config.json.example pr_agent/config.json
   ```

4. Ollamaを起動：
   ```bash
   ollama serve
   ```

## 使い方

### CLI
PRメッセージを生成：
```bash
python pr_agent/main.py pr --input "ログイン処理をリファクタリング"
```

マージメッセージを生成：
```bash
python pr_agent/main.py merge --input "feature/loginをマージ"
```

オプション：
- `--character`: キャラクター名またはインデックス（例: "煉獄杏寿郎"）
- `--input`: 変更内容（省略時は標準入力から読み込み）

### Web UI
Webインターフェースを起動：
```bash
streamlit run pr_agent/app.py
```
ブラウザで新しいタブが開きます。
1. サイドバーでキャラクターを選択・編集
2. 変更内容をテキストエリアに入力
3. 「PRメッセージを生成」または「マージメッセージを生成」をクリック

## 主な機能

### メッセージ生成
- キャラクターの口調・口癖を再現したPR/マージメッセージ生成
- 生成文字数の調整（目安文字数設定）
- 変更内容に基づいたコンテキスト理解

### キャラクター管理
- 複数キャラクターの登録・切り替え
- キャラクター詳細（口調・口癖）の自動生成（LLM使用）
- Web検索による実際のセリフ・名言の自動取得と保存
- 保存された名言の表示・確認

### Web検索機能（キャラクター詳細生成時）
- DuckDuckGoでキャラクターのセリフを検索
- 検索結果のページ内容をLLMで解析
- 実際のセリフのみを抽出（説明文・まとめ文を除外）
- 重複除外と最大5件のランダム選択
- 抽出されたセリフをキャラクター設定に自動保存

### モデル管理
- ローカルにインストール済みのOllamaモデル一覧表示
- モデルの切り替え（メモリからのアンロード機能付き）
- 人気モデルのダウンロード（進捗表示付き）
- カスタムモデル名でのダウンロード対応

### 設定
- インターネット検索の有効/無効切り替え
- 目安文字数の調整
- キャラクター情報の編集・削除

## 技術詳細

### セリフ抽出の仕組み
1. DuckDuckGoで「{キャラクター名} {作品名} セリフ」を検索（最大5ページ）
2. 各ページのHTMLを取得し、不要な要素（script、style等）を除去
3. ページ内容（最大3000文字）をLLMに渡してセリフのみを抽出
4. 以下の条件でフィルタリング：
   - 「」で囲まれている
   - 150文字以内
   - 説明文キーワード（「というセリフ」「性格は」等）を含まない
5. 重複を除外し、最大5件をランダム選択
6. キャラクター設定に保存

### 依存パッケージ
- `requests`: HTTP通信
- `beautifulsoup4`: HTML解析
- `ddgs`: DuckDuckGo検索
- `streamlit`: Web UI
- `typing-extensions`: 型ヒント

## デバッグ

コンソールに詳細なデバッグログが出力されます：
- 検索クエリと結果数
- 各ページからの抽出セリフ
- 重複除外後の件数
- LLMに渡される最終的なセリフ

## 設定ファイル

### デフォルト設定（config.json.example）
初回起動時は `config.json.example` を `config.json` にコピーしてください：
```bash
cp pr_agent/config.json.example pr_agent/config.json
```

`pr_agent/config.json`にキャラクター情報とモデル設定が保存されます：
```json
{
  "api_url": "http://localhost:11434/api/generate",
  "model": "llama3",
  "active_character_index": 0,
  "use_search": false,
  "target_length": 300,
  "characters": [
    {
      "name": "キャラクター名",
      "work": "作品名",
      "description": "口調・口癖の説明",
      "quotes": ["セリフ1", "セリフ2", ...]
    }
  ]
}
```
