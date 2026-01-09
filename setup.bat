@echo off
echo マーケティング分析AIエージェントのセットアップを開始します...

REM 1. PostgreSQLコンテナを起動
echo PostgreSQLコンテナを起動しています...
docker-compose up -d postgres

REM 2. データベースが起動するまで待機
echo データベースの起動を待機しています...
timeout /t 15 /nobreak

REM 3. データをインポート
echo データをインポートしています...
python import_data.py

REM 4. 全てのサービスを起動
echo 全てのサービスを起動しています...
docker-compose up -d --build

echo.
echo セットアップが完了しました！
echo フロントエンド: http://localhost:3000
echo バックエンドAPI: http://localhost:8000
echo.
echo 注意: OPENAI_API_KEYを環境変数またはbackend/.envファイルに設定してください

pause


