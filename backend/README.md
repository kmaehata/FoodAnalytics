# バックエンド API

## 環境変数

`.env` ファイルを作成して以下の環境変数を設定してください：

```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://marketing_user:marketing_pass@postgres:5432/marketing_db
```

## API エンドポイント

### POST /api/query

マーケティング分析クエリを処理します。

**リクエスト:**
```json
{
  "query": "20代の顧客の平均注文金額を教えて"
}
```

**レスポンス:**
```json
{
  "sql": "SELECT AVG(total_price) FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE customers.age BETWEEN 20 AND 29",
  "result": [
    {
      "avg": 2345.67
    }
  ],
  "summary": "分析結果のサマリー...",
  "error": null
}
```

### GET /health

ヘルスチェックエンドポイント

## 処理フロー

1. **入力検証（第1LLM）**: ユーザーの質問が適切かどうかを検証
2. **SQL生成（第2LLM）**: 質問からSQLクエリを生成
3. **SQL実行**: 生成されたSQLを実行
4. **サマリー生成**: 結果をテンプレート形式でまとめる


