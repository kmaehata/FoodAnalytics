# マーケティング分析AIエージェント

イタリアン風レストランのマーケティングデータを分析するAIエージェントアプリケーションです。

## 機能

- 自然言語での質問入力
- 入力内容の検証（第1LLM：不適切な質問をフィルタリング）
- SQLクエリの自動生成（第2LLM）
- SQL実行と結果取得
- 分析結果のテンプレート形式での出力

## 技術スタック

- **フロントエンド**: React, JavaScript
- **バックエンド**: Python, FastAPI
- **データベース**: PostgreSQL
- **AI**: OpenAI GPT-4
- **インフラ**: Docker, Docker Compose

## セットアップ

### 前提条件

- Docker と Docker Compose がインストールされていること
- OpenAI API キーが必要です

### 1. 環境変数の設定

`backend/.env` ファイルを作成し、OpenAI APIキーを設定してください：

```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://marketing_user:marketing_pass@postgres:5432/marketing_db
```

または、`docker-compose.yml` の環境変数セクションで直接設定することもできます。

### 2. データベースへのデータインポート

まず、PostgreSQLコンテナを起動してデータをインポートします：

```bash
# PostgreSQLコンテナのみ起動
docker-compose up -d postgres

# データベースが起動するまで待機（約10秒）
sleep 10

# データをインポート
python import_data.py
```

### 3. アプリケーションの起動

全てのサービスを起動します：

```bash
docker-compose up --build
```

または、バックグラウンドで起動する場合：

```bash
docker-compose up -d --build
```

### 4. アクセス

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 使用方法

1. ブラウザで http://localhost:3000 にアクセス
2. 自然言語で質問を入力（例：「20代の顧客の平均注文金額を教えて」）
3. 「分析実行」ボタンをクリック
4. 分析結果、実行されたSQL、データ結果が表示されます

## データ構造

### customers テーブル
- customer_id: 顧客ID
- age: 年齢（20-60歳）
- sex: 性別（man/woman）
- live: 居住エリア（日本の都道府県）

### items テーブル
- item_id: 商品ID
- price: 価格

### orders テーブル
- order_id: 注文ID
- customer_id: 顧客ID
- order_time: 注文日時
- total_price: 合計金額
- item_id: 商品ID

## 例文

- 「20代の顧客の平均注文金額を教えて」
- 「最も人気のある商品トップ5は？」
- 「東京都の顧客とその他の地域の顧客の平均年齢を比較して」
- 「月別の売上推移を教えて」
- 「性別ごとの平均注文金額を分析して」

## トラブルシューティング

### データベース接続エラー

PostgreSQLコンテナが起動しているか確認：

```bash
docker-compose ps
```

### OpenAI API エラー

`OPENAI_API_KEY` が正しく設定されているか確認してください。

### ポートが既に使用されている場合

`docker-compose.yml` のポート番号を変更してください。

## 開発

### バックエンドの開発

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### フロントエンドの開発

```bash
cd frontend
npm install
npm start
```

## ライセンス

MIT


