-- テーブル作成

-- 顧客テーブル
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    age INTEGER NOT NULL,
    sex VARCHAR(10) NOT NULL,
    live VARCHAR(50) NOT NULL
);

-- 商品テーブル
CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY,
    price INTEGER NOT NULL
);

-- 注文テーブル
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_time TIMESTAMP NOT NULL,
    total_price INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- インデックス作成（パフォーマンス向上のため）
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_item_id ON orders(item_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_time ON orders(order_time);


