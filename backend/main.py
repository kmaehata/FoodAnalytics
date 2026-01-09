from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import urllib.parse
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI
from dotenv import load_dotenv
import json

# .envファイルを読み込む（Docker環境でもローカル環境でも動作）
load_dotenv()
# 明示的にパスを指定（Dockerコンテナ内では/app/.env）
load_dotenv(dotenv_path='.env', override=False)

app = FastAPI(title="Marketing Analysis AI Agent")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース接続設定
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://marketing_user:marketing_pass@localhost:5432/marketing_db"
)

# OpenAI設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("警告: OPENAI_API_KEYが設定されていません。環境変数を設定してください。")

# OpenAIクライアントの初期化（APIキーがある場合のみ）
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"OpenAIクライアントの初期化エラー: {e}")
        client = None


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    sql: str
    result: list
    summary: str
    error: Optional[str] = None


def get_db_connection():
    """データベース接続を取得"""
    try:
        # URLをパースして個別のパラメータに分解
        parsed = urllib.parse.urlparse(DATABASE_URL)
        
        # データベース名を取得（パスの先頭の'/'を除去）
        database_name = parsed.path.lstrip('/')
        
        # デバッグ情報（本番環境では削除推奨）
        print(f"接続情報: host={parsed.hostname}, port={parsed.port or 5432}, database={database_name}, user={parsed.username}")
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=database_name,
            user=parsed.username,
            password=parsed.password
        )
        return conn
    except psycopg2.OperationalError as e:
        error_msg = f"データベース接続エラー: {str(e)}"
        print(f"接続エラー詳細: {error_msg}")
        print(f"使用したDATABASE_URL: {DATABASE_URL}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"予期しないエラー: {str(e)}"
        print(f"エラー詳細: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


def validate_query_with_llm(user_query: str) -> tuple:
    """
    第1LLM: ユーザーの入力が適切かどうかを検証
    不適切な質問（パスワード、ID、個人情報など）をフィルタリング
    """
    if not client:
        # LLMが利用できない場合は基本的な検証のみ
        forbidden_keywords = ['パスワード', 'password', 'ID', 'id', '個人情報', '秘密', '機密']
        if any(keyword in user_query.lower() for keyword in forbidden_keywords):
            return False, "この質問はセキュリティ上の理由で回答できません。"
        return True, ""
    
    system_prompt = """あなたはマーケティング分析のための質問検証システムです。
ユーザーの質問がマーケティング分析に関連する適切な質問かどうかを判断してください。

以下のような質問は拒否してください：
- パスワード、ID、個人情報に関する質問
- セキュリティに関わる質問
- データベースの構造や技術的な詳細を尋ねる質問
- マーケティング分析と無関係な質問

マーケティング分析に関連する質問（売上、顧客分析、商品分析など）は許可してください。

回答はJSON形式で、{"allowed": true/false, "reason": "理由"} の形式で返してください。"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        # JSONコードブロックから抽出（もしあれば）
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        result = json.loads(content)
        return result.get("allowed", False), result.get("reason", "")
    
    except Exception as e:
        print(f"LLM検証エラー: {e}")
        # エラー時は許可（フォールバック）
        return True, ""


def generate_sql_with_llm(user_query: str) -> str:
    """
    第2LLM: ユーザーの質問からSQLクエリを生成
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。"
        )
    
    schema_info = """
データベーススキーマ:
- customers テーブル: customer_id (INTEGER), age (INTEGER), sex (VARCHAR), live (VARCHAR)
- items テーブル: item_id (INTEGER), price (INTEGER)
- orders テーブル: order_id (INTEGER), customer_id (INTEGER), order_time (TIMESTAMP), total_price (INTEGER), item_id (INTEGER)

テーブル間の関係:
- orders.customer_id -> customers.customer_id
- orders.item_id -> items.item_id
"""
    
    system_prompt = f"""あなたはマーケティング分析のためのSQLクエリ生成エキスパートです。
ユーザーの質問に基づいて、PostgreSQL用のSQLクエリを生成してください。

{schema_info}

重要なルール:
1. SELECT文のみを生成してください（INSERT、UPDATE、DELETEは禁止）
2. 適切なJOINを使用してテーブルを結合してください
3. 集計関数（SUM、COUNT、AVGなど）を適切に使用してください
4. 日付の処理にはPostgreSQLの関数を使用してください
5. クエリは実行可能で安全なものにしてください

SQLクエリのみを返してください。説明やコメントは不要です。"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3
        )
        
        sql = response.choices[0].message.content.strip()
        # SQLコードブロックから抽出
        if sql.startswith("```"):
            sql = sql.split("```")[1]
            if sql.startswith("sql"):
                sql = sql[3:]
            sql = sql.strip()
        
        return sql
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL生成エラー: {str(e)}")


def execute_sql(sql: str) -> list:
    """SQLクエリを実行して結果を返す"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        results = cursor.fetchall()
        # 辞書形式に変換
        return [dict(row) for row in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL実行エラー: {str(e)}")
    finally:
        conn.close()


def generate_summary_with_llm(user_query: str, sql: str, results: list) -> str:
    """結果をテンプレート形式でまとめる"""
    print(f"generate_summary_with_llm開始: client={client is not None}, results数={len(results)}")
    
    if not client:
        print("OpenAIクライアントが利用できません。フォールバックサマリーを返します。")
        return f"クエリ結果: {len(results)}件のデータが取得されました。"
    
    print("システムプロンプト作成中...")
    system_prompt = """あなたはマーケティング分析の専門家です。
SQLクエリの実行結果を分析し、ビジネスに役立つ洞察を含む分かりやすいレポートを作成してください。

レポートには以下を含めてください：
1. 分析結果の要約
2. 重要な数値や傾向
3. ビジネスへの示唆や推奨事項

日本語で、分かりやすく、専門的すぎない表現で書いてください。"""

    print("結果データをJSONに変換中...")
    try:
        results_str = json.dumps(results, ensure_ascii=False, indent=2)
        print(f"JSON変換成功: 長さ={len(results_str)}")
    except Exception as e:
        print(f"JSON変換エラー: {e}")
        results_str = str(results)
    
    prompt = f"""
ユーザーの質問: {user_query}

実行されたSQL: {sql}

結果データ:
{results_str}

上記の結果を分析して、マーケティング分析レポートを作成してください。
"""
    
    try:
        print(f"サマリー生成リクエスト送信: ユーザークエリ={user_query}, 結果数={len(results)}")
        print(f"プロンプト長: {len(prompt)}")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        print("OpenAI APIレスポンス受信")
        
        summary = response.choices[0].message.content
        print(f"サマリー生成成功: 長さ={len(summary) if summary else 0}")
        if summary:
            print(f"サマリー先頭50文字: {summary[:50]}")
        return summary if summary else f"分析結果: {len(results)}件のデータが取得されました。詳細は結果データを参照してください。"
    
    except Exception as e:
        print(f"サマリー生成エラー: {e}")
        import traceback
        traceback.print_exc()
        return f"分析結果: {len(results)}件のデータが取得されました。詳細は結果データを参照してください。"


@app.get("/")
def read_root():
    return {"message": "Marketing Analysis AI Agent API"}


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    メインのクエリ処理エンドポイント
    1. 入力検証（第1LLM）
    2. SQL生成（第2LLM）
    3. SQL実行
    4. 結果のサマリー生成
    """
    try:
        # ステップ1: 入力検証
        print(f"クエリ受信: {request.query}")
        allowed, reason = validate_query_with_llm(request.query)
        print(f"検証結果: allowed={allowed}, reason={reason}")
        if not allowed:
            raise HTTPException(
                status_code=400,
                detail=f"この質問は回答できません: {reason}"
            )
        
        # ステップ2: SQL生成
        print("SQL生成を開始...")
        sql = generate_sql_with_llm(request.query)
        print(f"生成されたSQL: {sql}")
        
        # ステップ3: SQL実行
        print("SQL実行を開始...")
        results = execute_sql(sql)
        print(f"取得した結果数: {len(results)}")
        
        # ステップ4: サマリー生成
        print("サマリー生成を開始...")
        summary = generate_summary_with_llm(request.query, sql, results)
        print(f"生成されたサマリー長: {len(summary) if summary else 0}")
        
        return QueryResponse(
            sql=sql,
            result=results,
            summary=summary,
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return QueryResponse(
            sql="",
            result=[],
            summary="",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

