# voice-ai-chat-agent-backend

<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/README.md"><img alt="README in English" src="https://img.shields.io/badge/English-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-CN.md"><img alt="简体中文操作指南" src="https://img.shields.io/badge/简体中文-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-JP.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-KR.md"><img alt="README in 한국어" src="https://img.shields.io/badge/한국어-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-ES.md"><img alt="README en Español" src="https://img.shields.io/badge/Español-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-FR.md"><img alt="README en Français" src="https://img.shields.io/badge/Français-lightgrey"></a>
<a href="https://github.com/neothan-dev/voice-ai-chat-agent-backend/blob/main/doc/README-IT.md"><img alt="README in Italiano" src="https://img.shields.io/badge/Italiano-lightgrey"></a>

FastAPI ベースの AI 音声チャット バックエンド サービス。リアルタイム音声インタラクション、ユーザー管理、データ設定、クラウドデプロイをサポートします。

## ✨ 特長

- 🎤 **リアルタイム音声インタラクション**: 音声認識 (STT) と音声合成 (TTS) に対応
- 🤖 **AI 対話**: OpenAI GPT モデルを統合し、インテリジェントな会話を提供
- 👤 **ユーザー管理**: ユーザー登録、ログイン、セッション管理を提供
- 📊 **データ設定**: Excel ファイルで柔軟にアプリデータを設定
- 🌐 **WebSocket 対応**: リアルタイムの双方向通信
- 🚀 **ワンクリックデプロイ**: Google Cloud Run へのワンクリックデプロイに対応
- 🔧 **拡張可能なアーキテクチャ**: モジュール化設計で拡張が容易

## 🏗️ アーキテクチャ

```
├── api/                    # API ルートモジュール
│   ├── auth.py          # ユーザー認証
│   ├── ai.py            # AI 対話エンドポイント
│   ├── speech.py        # 音声処理
│   ├── navigation.py    # ナビゲーション機能
│   ├── dashboard.py     # ダッシュボード
│   ├── device.py       # デバイス管理
│   └── health.py       # ヘルスチェック
├── core/                 # コアモジュール
│   ├── config.py       # 設定管理
│   └── db.py           # データベース接続
├── models/              # データモデル
│   ├── user.py         # ユーザーモデル
│   ├── session.py      # セッションモデル
│   └── health_data.py  # ヘルスデータモデル
├── services/            # ビジネスサービス
│   ├── ai_comprehensive_service.py  # AI 総合サービス
│   ├── stt_service.py  # 音声からテキスト
│   ├── tts_service.py  # テキストから音声
│   ├── emotion_service.py  # 感情分析
│   ├── translation_service.py  # 翻訳サービス
│   └── ...
├── utils/               # ユーティリティ
│   ├── config_manager.py  # 設定ローダー
│   └── excel_to_code.py   # Excel からコード
├── dev/data/           # 開発データ
│   ├── excel/          # Excel 設定ファイル
│   └── code/           # 生成された設定コード
└── main.py             # アプリケーションエントリポイント
```

## 🚀 クイックスタート

### 動作要件

- Python 3.8+
- PostgreSQL 12+
- 各種 AI サービスの API キー

### インストール手順

1. **プロジェクトをクローン**
```bash
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend
```

2. **仮想環境を作成**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

3. **依存関係をインストール**
```bash
pip install -r requirements.txt
```

4. **環境変数を設定**
```bash
cp env_example.txt .env
```

`.env` を編集し、必要な API キーを設定します:

```env
# データベース設定
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_ai_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Azure Cognitive Services
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_EMOTION_KEY=your_azure_emotion_key_here
AZURE_EMOTION_ENDPOINT=your_azure_emotion_endpoint_here

# Google Cloud API
GOOGLE_APPLICATION_CREDENTIALS=credential/your_google_cloud_credential.json

# その他の設定...
```

5. **データベースを初期化**
```bash
# PostgreSQL サービスが稼働していることを確認
# データベースを作成
createdb voice_ai_db

# アプリを実行（自動でデータベースを初期化）
python main.py
```

6. **サービスを起動**
```bash
# 開発モード
python main.py

# または uvicorn を使用
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`http://localhost:8000/docs` にアクセスして API ドキュメントを確認できます。

## 📋 設定

### 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `DATABASE_URL` | データベース接続 URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API キー | ✅ |
| `AZURE_SPEECH_KEY` | Azure 音声サービスキー | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud 認証ファイルパス | ✅ |
| `SECRET_KEY` | JWT 認証シークレット | ✅ |
| `HOST` | サーバーホスト | ❌ |
| `PORT` | サーバーポート | ❌ |
| `DEBUG` | デバッグモード | ❌ |

### Excel 設定システム

本プロジェクトは Excel ファイルによるアプリデータ設定をサポートし、柔軟なデータ管理を実現します:

1. **Excel ファイルを作成**: `dev/data/excel/` ディレクトリに `.xlsx` ファイルを作成
2. **データを設定**: テンプレート形式に従ってデータを入力
3. **自動変換**: システムが Excel を自動的に Python 設定コードへ変換
4. **動的ロード**: ホットリロード対応。Excel 変更後に設定を自動更新

#### 設定ローダーの使用

```python
from utils.config_manager import CONFIG_LOADER

# 設定を取得
config = CONFIG_LOADER.get_config('navigation')

# 特定のシートの設定を取得
sheet_config = CONFIG_LOADER.get_config_sheet('navigation', 'routes')

# 特定の設定値を取得
value = CONFIG_LOADER.get_config_value('navigation', 'routes', 'home_path')
```

## 🔧 API エンドポイント

### 認証

- `POST /auth/register` - ユーザー登録
- `POST /auth/login` - ログイン
- `POST /auth/refresh` - トークン更新
- `GET /auth/me` - 現在のユーザー情報取得

### AI 対話

- `POST /ai/chat` - チャットメッセージ送信
- `WebSocket /ai/chat/ws` - リアルタイムチャット接続
- `GET /ai/history` - チャット履歴取得

### 音声

- `POST /speech/stt` - 音声からテキスト
- `POST /speech/tts` - テキストから音声
- `WebSocket /speech/ws` - リアルタイム音声ストリーム

### ナビゲーション

- `GET /navigation/routes` - ナビゲーションルート取得
- `POST /navigation/update` - ナビゲーション設定更新

## 🐳 Docker デプロイ

### ローカルで Docker 実行

```bash
# イメージをビルド
docker build -t voice-ai-chat-agent-backend .

# コンテナを実行
docker run -p 8000:8000 --env-file .env voice-ai-chat-agent-backend
```

### Docker Compose

```bash
# すべてのサービスを起動
docker-compose up -d

# ログを表示
docker-compose logs -f
```

## ☁️ Google Cloud デプロイ

### ワンクリックデプロイ

```bash
# Google Cloud CLI を設定
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# デプロイスクリプトを実行
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

### 手動デプロイ

1. **イメージをビルド**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend
```

2. **Cloud Run にデプロイ**
```bash
gcloud run deploy voice-ai-chat-agent-backend \
  --image gcr.io/YOUR_PROJECT_ID/voice-ai-chat-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 テスト

```bash
# テストを実行
pytest

# 特定のテストを実行
pytest tests/test_auth.py

# カバレッジレポートを生成
pytest --cov=api --cov-report=html
```

## 📊 監視とログ

### ログ設定

ログファイルの場所: `logs/app.log`

ログレベルは環境変数 `LOG_LEVEL` で設定可能です。

## 🔒 セキュリティ考慮事項

- JWT トークン認証
- パスワードのハッシュ化と保存
- CORS 設定
- 環境変数で機密情報を保護
- API レート制限（設定可能）

## 🤝 貢献ガイド

1. リポジトリを Fork
2. 機能ブランチを作成（`git checkout -b feature/AmazingFeature`）
3. 変更をコミット（`git commit -m 'Add some AmazingFeature'`）
4. ブランチをプッシュ（`git push origin feature/AmazingFeature`）
5. Pull Request を作成

## 📝 開発ガイド

### 新しい API エンドポイントの追加

1. `api/` に新しいルートファイルを作成
2. `main.py` にルートを登録
3. 必要に応じてデータモデルを追加
4. テストケースを作成

### 新しい設定の追加

1. `dev/data/excel/` に Excel ファイルを作成
2. テンプレート形式に従ってデータを設定
3. `CONFIG_LOADER` を使用して設定を読み込む

### コーディング規約

- 型ヒントを使用
- PEP 8 に準拠
- 適切なドキュメンテーション文字列を追加
- ユニットテストを作成

## 🐛 トラブルシューティング

### よくある問題

1. **データベース接続に失敗**
   - PostgreSQL が稼働しているか確認
   - 接続 URL を確認
   - データベースユーザーの権限を確認

2. **API キーのエラー**
   - 環境変数設定を確認
   - API キーの有効性を確認
   - サービスのクォータを確認

3. **Excel 設定が反映されない**
   - Excel ファイル形式を確認
   - ファイルパスが正しいか確認
   - 変換ログを確認

## 📄 ライセンス

本プロジェクトは Apache 2.0 ライセンス - 詳細は [LICENSE](LICENSE) を参照してください。

Apache 2.0 は次を提供します:
- ✅ 特許保護
- ✅ 商標保護  
- ✅ より強力な法的保護
- ✅ エンタープライズレベルの標準

## 🙏 謝辞

- [FastAPI](https://fastapi.tiangolo.com/) - モダンで高速な Web フレームワーク
- [OpenAI](https://openai.com/) - AI モデルサービス
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/) - 音声と感情分析
- [Google Cloud](https://cloud.google.com/) - クラウドサービスのサポート

## 📞 サポート

質問や提案がある場合は:

1. [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues) を確認
2. 新しい Issue を作成
3. メンテナに連絡

---

⭐ このプロジェクトが役立った場合はスターをお願いします！
