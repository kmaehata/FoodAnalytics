import csv
import psycopg2
import os
from datetime import datetime

# データベース接続情報
# Docker環境では 'postgres'、ローカルでは 'localhost'
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_CONFIG = {
    'host': DB_HOST,
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'marketing_db'),
    'user': os.getenv('DB_USER', 'marketing_user'),
    'password': os.getenv('DB_PASSWORD', 'marketing_pass')
}

def import_csv_to_db(csv_file, table_name, columns, connection):
    """CSVファイルをデータベースにインポート"""
    cursor = connection.cursor()
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        if not rows:
            print(f'{csv_file} は空です')
            return
        
        # テーブルをクリア
        cursor.execute(f'TRUNCATE TABLE {table_name} CASCADE')
        
        # データを挿入
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        for row in rows:
            values = [row[col] for col in columns]
            query = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
            cursor.execute(query, values)
        
        connection.commit()
        print(f'{table_name} に {len(rows)} レコードをインポートしました')

def main():
    print('データベースへのデータインポートを開始します...')
    
    try:
        # データベースに接続
        conn = psycopg2.connect(**DB_CONFIG)
        print('データベースに接続しました')
        
        # 各CSVファイルをインポート
        import_csv_to_db('customers.csv', 'customers', 
                        ['customer_id', 'age', 'sex', 'live'], conn)
        
        import_csv_to_db('items.csv', 'items', 
                        ['item_id', 'price'], conn)
        
        import_csv_to_db('orders.csv', 'orders', 
                        ['order_id', 'customer_id', 'order_time', 'total_price', 'item_id'], conn)
        
        # 統計情報を表示
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM customers')
        customer_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM items')
        item_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM orders')
        order_count = cursor.fetchone()[0]
        
        print(f'\nインポート完了:')
        print(f'  顧客: {customer_count} レコード')
        print(f'  商品: {item_count} レコード')
        print(f'  注文: {order_count} レコード')
        
        conn.close()
        print('\nデータインポートが正常に完了しました！')
        
    except Exception as e:
        print(f'エラーが発生しました: {e}')
        raise

if __name__ == '__main__':
    main()

