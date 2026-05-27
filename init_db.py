import csv
import os
import sqlite3

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CSV 路径
PRODUCT_FILE = os.path.join(BASE_DIR, "data", "products.csv")
ORDER_FILE = os.path.join(BASE_DIR, "data", "orders.csv")

# 数据库路径
DB_FILE = os.path.join(BASE_DIR, "customer_service.db")


def init_database():

    # 如果数据库已存在，先删除
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # =========================
    # 创建商品表
    # =========================
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price REAL,
            stock INTEGER,
            aliases TEXT
        )
    """)

    # =========================
    # 创建订单表
    # =========================
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            product_name TEXT,
            pay_amount REAL,
            order_status TEXT,
            logistics_company TEXT,
            tracking_number TEXT,
            shipping_status TEXT
        )
    """)

    # =========================
    # 导入商品数据
    # =========================
    with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO products (name, category, price, stock, aliases)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row["name"],
                row["category"],
                float(row["price"]),
                int(row["stock"]),
                row["aliases"]
            ))

    # =========================
    # 导入订单数据
    # =========================
    with open(ORDER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO orders (
                    order_id,
                    product_name,
                    pay_amount,
                    order_status,
                    logistics_company,
                    tracking_number,
                    shipping_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["order_id"],
                row["product_name"],
                float(row["pay_amount"]),
                row["order_status"],
                row["logistics_company"],
                row["tracking_number"],
                row["shipping_status"]
            ))

    # 提交并关闭
    conn.commit()
    conn.close()

    print("数据库初始化完成：customer_service.db")


if __name__ == "__main__":
    init_database()