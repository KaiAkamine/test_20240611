# PR Message Generator - 設計書

## 1. システム概要

### 1.1 目的
ローカルLLM（Ollama）を使用して、キャラクターになりきったPR・マージメッセージを自動生成するツール。

### 1.2 主要機能
- キャラクター口調でのPR/マージメッセージ生成
- 複数キャラクターの管理（追加・編集・削除・切り替え）
- Web検索によるキャラクターセリフの自動収集
- Ollamaモデルの管理（一覧表示・切り替え・ダウンロード）
- CLI/Web UI両対応

### 1.3 技術スタック
- **言語**: Python 3.8+
- **LLM**: Ollama (ローカル実行)
- **Web UI**: Streamlit
- **Web検索**: DuckDuckGo Search (ddgs)
- **HTML解析**: BeautifulSoup4
- **HTTP通信**: requests, urllib

---

## 2. アーキテクチャ

### 2.1 ディレクトリ構成
```
test_20240611/
├── pr_agent/
│   ├── app.py              # Streamlit Web UI
│   ├── client.py           # Ollama API クライアント
│   ├── main.py             # CLI エントリーポイント
│   ├── prompts.py          # プロンプトテンプレート
│   ├── search.py           # Web検索・セリフ抽出
│   ├── utils.py            # ユーティリティ関数
│   ├── config.json         # ユーザー設定（gitignore対象）
│   └── config.json.example # デフォルト設定テンプレート
├── requirements.txt        # 依存パッケージ
├── README.md              # ユーザー向けドキュメント
├── DESIGN.md              # 本設計書
└── .gitignore             # Git除外設定
```

### 2.2 モジュール構成

#### 2.2.1 client.py - Ollama API クライアント
**責務**: Ollama APIとの通信を抽象化

**主要クラス**: `OllamaClient`

**メソッド**:
- `generate_text(prompt: str, model: Optional[str]) -> str`
  - テキスト生成（ストリーミングなし）
  - 16進数バイト表現の除去処理を含む
- `check_connection() -> bool`
  - Ollama接続確認
- `list_local_models() -> List[Dict[str, str]]`
  - ローカルモデル一覧取得
- `pull_model(model_name: str, progress_callback) -> bool`
  - モデルダウンロード（進捗コールバック付き）
- `unload_model(model_name: str) -> bool`
  - モデルのメモリアンロード
- `get_popular_models() -> List[Dict[str, str]]` (static)
  - 人気モデルリスト取得

**依存**: urllib, json

#### 2.2.2 prompts.py - プロンプト管理
**責務**: LLMへのプロンプト生成

**定数**:
- `PR_SYSTEM_PROMPT`: PRメッセージ生成用テンプレート

**関数**:
- `get_messages(character_config: dict, inputs: str, search_context: str, target_length: int) -> str`
  - キャラクター設定と入力を元にプロンプト生成
  - 検索コンテキストの追加サポート

#### 2.2.3 search.py - Web検索・セリフ抽出
**責務**: キャラクターセリフのWeb検索と抽出

**関数**:
- `search_quotes(character: str, work: str, client: OllamaClient) -> List[str]`
  - DuckDuckGoで検索（最大5ページ）
  - 各ページからセリフ抽出
- `extract_quotes_from_page(url: str, character: str, client: OllamaClient) -> List[str]`
  - HTML取得・パース
  - LLMによるセリフ抽出
- `extract_quotes_with_llm(text: str, character: str, client: OllamaClient) -> List[str]`
  - テキストから実際のセリフのみを抽出
  - 説明文・メタ情報のフィルタリング
- `get_random_quote_context(character: str, work: str) -> Tuple[str, List[str]]`
  - ランダムに5件選択してコンテキスト文字列生成
  - 重複除外処理

**依存**: ddgs, requests, BeautifulSoup4, client.py

#### 2.2.4 utils.py - ユーティリティ
**責務**: 共通処理の提供

**関数**:
- `generate_character_prompt(character_name: str, work_name: str, quote_context: str) -> str`
  - キャラクター詳細生成用プロンプト作成
  - 重複コード削減のための共通化

#### 2.2.5 app.py - Web UI
**責務**: Streamlitベースのユーザーインターフェース

**主要機能**:
- キャラクター選択・切り替え
- PR/マージメッセージ生成
- キャラクター編集・追加・削除
- モデル管理UI
- 設定管理（検索有効化、目安文字数）

**セッション状態管理**:
- `edit_char_desc`: 編集中のキャラクター説明
- `edit_char_quotes`: 編集中のセリフリスト
- `temp_char_*`: 新規追加中のキャラクター情報

**依存**: 全モジュール

#### 2.2.6 main.py - CLI
**責務**: コマンドライン実行

**引数**:
- `command`: pr | merge
- `--input, -i`: 変更内容（省略時は標準入力）
- `--character, -c`: キャラクター名またはインデックス

**依存**: client.py, prompts.py, search.py

---

## 3. データモデル

### 3.1 config.json 構造
```json
{
  "model": "qwen2.5:14b",
  "api_url": "http://localhost:11434/api/generate",
  "active_character_index": 0,
  "use_search": false,
  "target_length": 300,
  "characters": [
    {
      "name": "キャラクター名",
      "work": "作品名",
      "description": "口調・口癖の説明",
      "quotes": ["セリフ1", "セリフ2"]  // オプション
    }
  ]
}
```

**フィールド説明**:
- `model`: 使用するOllamaモデル名
- `api_url`: Ollama API エンドポイント
- `active_character_index`: 現在選択中のキャラクターインデックス
- `use_search`: Web検索の有効/無効
- `target_length`: 生成メッセージの目安文字数
- `characters`: キャラクター配列
  - `name`: キャラクター名（必須）
  - `work`: 作品名（必須）
  - `description`: 口調・性格の説明（必須）
  - `quotes`: 実際のセリフリスト（オプション、Web検索で自動追加）

---

## 4. 処理フロー

### 4.1 PRメッセージ生成フロー
```
1. ユーザー入力（変更内容）
2. キャラクター設定読み込み
3. [オプション] Web検索でセリフ取得
4. プロンプト生成
   - キャラクター設定
   - 変更内容
   - 検索コンテキスト（あれば）
   - 目安文字数
5. Ollama API呼び出し
6. レスポンス整形（16進数除去）
7. 結果表示
```

### 4.2 キャラクター詳細自動生成フロー
```
1. キャラクター名・作品名入力
2. Web検索実行
   a. DuckDuckGo検索（最大5ページ）
   b. 各ページHTML取得
   c. 不要要素除去（script, style等）
   d. LLMでセリフ抽出
   e. フィルタリング
      - 「」で囲まれている
      - 150文字以内
      - 説明文キーワード除外
3. 重複除外
4. ランダム5件選択
5. LLMで口調・性格説明生成
6. config.jsonに保存
```

### 4.3 モデル切り替えフロー
```
1. ローカルモデル一覧取得
2. ユーザーが新モデル選択
3. 現在のモデルをアンロード
4. config.jsonに新モデル保存
5. UI再読み込み
```

---

## 5. セキュリティ・ベストプラクティス

### 5.1 設定ファイル管理
- `config.json`は`.gitignore`に追加（ユーザー固有設定のため）
- `config.json.example`をテンプレートとして提供
- 初回起動時にコピーを促す

### 5.2 依存パッケージ
- バージョン指定（`requirements.txt`）
  - セキュリティアップデート追跡
  - 再現性確保

### 5.3 エラーハンドリング
- Ollama接続失敗時の明確なエラーメッセージ
- Web検索失敗時のフォールバック（LLM知識のみで生成）
- 不正なconfig.json時の適切なエラー表示

### 5.4 入力検証
- キャラクター名・作品名の空チェック
- モデル名の存在確認
- インデックス範囲チェック

---

## 6. 拡張性

### 6.1 新機能追加ポイント
- **新しいLLMプロバイダー対応**: `client.py`に新クラス追加
- **新しい検索エンジン対応**: `search.py`に新関数追加
- **新しいメッセージタイプ**: `prompts.py`に新テンプレート追加
- **新しいUI**: 新しいエントリーポイント作成（app.pyを参考）

### 6.2 設定拡張
- `config.json`に新フィールド追加可能
- 後方互換性のためデフォルト値設定推奨

---

## 7. テスト戦略

### 7.1 単体テスト対象
- `client.py`: API通信、テキスト整形
- `search.py`: セリフ抽出ロジック、フィルタリング
- `prompts.py`: プロンプト生成
- `utils.py`: ユーティリティ関数

### 7.2 統合テスト
- CLI実行（main.py）
- Web UI操作（app.py）
- Ollama接続テスト（diagnose_ollama.py）

### 7.3 手動テスト
- 各種キャラクターでのメッセージ生成品質確認
- Web検索結果の妥当性確認
- UI操作性確認

---

## 8. パフォーマンス考慮事項

### 8.1 Web検索
- 最大5ページに制限（過度なリクエスト防止）
- タイムアウト設定（5秒）
- 並列処理なし（シンプルさ優先）

### 8.2 LLM呼び出し
- ストリーミングなし（シンプルさ優先）
- モデルアンロード機能（メモリ節約）
- プロンプト長制限（3000文字）

### 8.3 UI
- Streamlit再読み込み最小化
- セッション状態活用

---

## 9. 既知の制約・制限

### 9.1 技術的制約
- Ollamaがローカルで起動している必要がある
- Python 3.8以上必須
- インターネット接続必須（Web検索使用時）

### 9.2 機能的制約
- 日本語キャラクターに最適化
- セリフ抽出精度はLLM性能に依存
- 検索結果の品質はWeb上の情報に依存

### 9.3 スケーラビリティ
- 単一ユーザー・ローカル実行想定
- 大量キャラクター登録時のUI性能未検証

---

## 10. 今後の改善案

### 10.1 短期
- [ ] ユニットテスト追加
- [ ] エラーメッセージの多言語対応
- [ ] ログ出力の構造化

### 10.2 中期
- [ ] キャラクターのインポート/エクスポート機能
- [ ] メッセージ生成履歴の保存
- [ ] カスタムプロンプトテンプレート機能

### 10.3 長期
- [ ] 複数LLMプロバイダー対応（OpenAI, Anthropic等）
- [ ] Git統合（自動PR作成）
- [ ] チーム共有機能（キャラクター設定の共有）

---

## 11. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2024-XX-XX | 1.0.0 | 初版作成 |
| 2024-XX-XX | 1.1.0 | リファクタリング（utils.py追加、型ヒント修正、依存バージョン指定） |

---

## 12. 参考資料

- [Ollama公式ドキュメント](https://github.com/ollama/ollama)
- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [DuckDuckGo Search Python](https://github.com/deedy5/duckduckgo_search)
