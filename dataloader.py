import csv
import os
#这个文件专门把 data 文件夹里的数据读进程序，它不负责回答问题，也不负责判断意图。


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_FILE = os.path.join(BASE_DIR, "data", "products.csv")
POLICY_FILE = os.path.join(BASE_DIR, "data", "policy.txt")
ORDER_FILE = os.path.join(BASE_DIR, "data", "orders.csv")


def load_products():
    """读取商品 CSV 数据"""
    products = []

    with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["price"] = float(row["price"])
            row["stock"] = int(row["stock"])
            row["aliases"] = row["aliases"].split("|")
            products.append(row)

    return products


def load_orders():
    """读取订单 CSV 数据"""
    orders = []

    with open(ORDER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["pay_amount"] = float(row["pay_amount"])
            orders.append(row)

    return orders


def load_policy():
    """读取售后政策文本"""
    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return f.read()