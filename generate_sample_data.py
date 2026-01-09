import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict

# 日本の都道府県リスト
PREFECTURES = [
    '東京都', '神奈川県', '埼玉県', '千葉県', '大阪府', '京都府', '兵庫県', 
    '愛知県', '福岡県', '北海道', '宮城県', '広島県', '新潟県', '静岡県',
    '長野県', '福島県', '茨城県', '群馬県', '栃木県', '岐阜県', '三重県',
    '滋賀県', '奈良県', '和歌山県', '岡山県', '山口県', '徳島県', '香川県',
    '愛媛県', '高知県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県',
    '鹿児島県', '沖縄県', '青森県', '岩手県', '秋田県', '山形県', '富山県',
    '石川県', '福井県', '山梨県', '鳥取県', '島根県'
]

# イタリアン料理メニュー（20種類）
MENU_ITEMS = [
    'マルゲリータピザ',
    'カルボナーラ',
    'アマトリチャーナ',
    'ペンネ・アラビアータ',
    'ミラノ風カツレツ',
    'ロブスターリゾット',
    'トリュフパスタ',
    'マリナーラピザ',
    'ラザニア',
    'オッソブーコ',
    'ティラミス',
    'カプレーゼ',
    'カルパッチョ',
    'アランチーニ',
    'ミネストローネ',
    'カチョ・エ・ペペ',
    'ナポリタン',
    'シーフードパエリア',
    'バーニャ・カウダ',
    'ポレンタ'
]

def generate_customers(num_records: int = 100) -> List[Dict]:
    """顧客データを生成"""
    customers = []
    # 東京を9割、その他を1割にするための重み付け
    tokyo_probability = 0.9
    
    for i in range(1, num_records + 1):
        age = random.randint(20, 60)
        sex = random.choice(['man', 'woman'])
        
        # 東京9割、その他1割
        if random.random() < tokyo_probability:
            live = '東京都'
        else:
            live = random.choice([p for p in PREFECTURES if p != '東京都'])
        
        customers.append({
            'customer_id': i,
            'age': age,
            'sex': sex,
            'live': live
        })
    
    return customers

def generate_items(num_records: int = 20) -> List[Dict]:
    """商品データを生成"""
    items = []
    
    # 各メニューに価格を設定（500円〜3000円の範囲でランダム）
    for i, menu_name in enumerate(MENU_ITEMS, 1):
        # より現実的な価格設定
        if 'ピザ' in menu_name:
            price = random.randint(1200, 2500)
        elif 'パスタ' in menu_name or 'リゾット' in menu_name or 'ラザニア' in menu_name:
            price = random.randint(1400, 2800)
        elif 'ステーキ' in menu_name or 'カツレツ' in menu_name or 'オッソブーコ' in menu_name:
            price = random.randint(2000, 3500)
        elif 'ティラミス' in menu_name:
            price = random.randint(600, 1000)
        elif 'サラダ' in menu_name or 'カルパッチョ' in menu_name or 'カプレーゼ' in menu_name:
            price = random.randint(800, 1500)
        elif 'パエリア' in menu_name:
            price = random.randint(1800, 3200)
        else:
            price = random.randint(1000, 2500)
        
        items.append({
            'item_id': i,
            'price': price
        })
    
    return items

def generate_orders(num_records: int = 1000, num_customers: int = 100, num_items: int = 20, items: List[Dict] = None) -> List[Dict]:
    """注文データを生成"""
    orders = []
    
    # 過去1年間の期間でランダムに注文日時を生成
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(1, num_records + 1):
        customer_id = random.randint(1, num_customers)
        item_id = random.randint(1, num_items)
        
        # ランダムな日時を生成
        random_days = random.randint(0, 365)
        random_hours = random.randint(10, 22)  # レストランの営業時間
        random_minutes = random.randint(0, 59)
        order_time = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        # 商品の価格を取得
        item_price = items[item_id - 1]['price'] if items else 0
        
        # 1注文で1-3個の商品を注文する可能性を考慮（簡略化のため1商品1注文とするが、合計金額は1-3倍にする）
        quantity = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
        total_price = item_price * quantity
        
        orders.append({
            'order_id': i,
            'customer_id': customer_id,
            'order_time': order_time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_price': total_price,
            'item_id': item_id
        })
    
    return orders

def write_csv(filename: str, data: List[Dict], fieldnames: List[str]):
    """CSVファイルに書き込み"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f'{filename} を作成しました ({len(data)}レコード)')

def main():
    print('サンプルデータの生成を開始します...')
    
    # 商品データを生成（注文データ生成時に価格が必要なため先に生成）
    items = generate_items(20)
    write_csv('items.csv', items, ['item_id', 'price'])
    
    # 顧客データを生成
    customers = generate_customers(100)
    write_csv('customers.csv', customers, ['customer_id', 'age', 'sex', 'live'])
    
    # 注文データを生成
    orders = generate_orders(1000, 100, 20, items)
    write_csv('orders.csv', orders, ['order_id', 'customer_id', 'order_time', 'total_price', 'item_id'])
    
    print('\n全てのサンプルデータの生成が完了しました！')
    print('生成されたファイル:')
    print('  - customers.csv (100レコード)')
    print('  - orders.csv (1000レコード)')
    print('  - items.csv (20レコード)')

if __name__ == '__main__':
    main()

