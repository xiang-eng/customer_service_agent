# ================================
# db_tools.py
# 作用：
# 提供基于 SQLite 的商品 / 订单查询函数
# 这一版从“全表读取 + Python 遍历”
# 升级成“SQL 条件查询”
# ================================

import os
import sqlite3


# 获取当前项目目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库文件路径
DB_FILE = os.path.join(BASE_DIR, "customer_service.db")


def get_connection():
    """
    创建数据库连接

    返回：
    - SQLite 连接对象
    """
    return sqlite3.connect(DB_FILE)


def row_to_product_dict(row):
    """
    把数据库中的商品记录转换成字典格式
    这样可以和原来系统里用的 product 结构保持一致
    """

    if row is None:
        return None

    return {
        "name": row[0],
        "category": row[1],
        "price": float(row[2]),
        "stock": int(row[3]),
        "aliases": row[4].split("|") if row[4] else []
    }


def row_to_order_dict(row):
    """
    把数据库中的订单记录转换成字典格式
    """

    if row is None:
        return None

    return {
        "order_id": row[0],
        "product_name": row[1],
        "pay_amount": float(row[2]),
        "order_status": row[3],
        "logistics_company": row[4],
        "tracking_number": row[5],
        "shipping_status": row[6],
    }


def find_product_in_db(question):
    """
    根据用户问题，从数据库中查商品

    查询顺序：
    1. 先按商品全名模糊匹配
    2. 再按商品类别模糊匹配
    3. 最后按 aliases 字段模糊匹配

    参数：
    - question：用户问题

    返回：
    - 商品字典；如果查不到，返回 None
    """

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # 1. 按商品全名查
    # =========================
    # instr(?, name) > 0 的意思：
    # 如果“用户问题”里包含商品名，就命中
    cursor.execute("""
        SELECT name, category, price, stock, aliases
        FROM products
        WHERE instr(?, name) > 0
        LIMIT 1
    """, (question,))

    row = cursor.fetchone()
    if row:
        conn.close()
        return row_to_product_dict(row)

    # =========================
    # 2. 按商品类别查
    # =========================
    cursor.execute("""
        SELECT name, category, price, stock, aliases
        FROM products
        WHERE instr(?, category) > 0
        LIMIT 1
    """, (question,))

    row = cursor.fetchone()
    if row:
        conn.close()
        return row_to_product_dict(row)

    # =========================
    # 3. 按 aliases 查
    # =========================
    # aliases 还是一个字符串，例如：
    # "小米音箱|音箱|智能音箱"
    # 所以这里只能先用 SQL 取出候选，再在 Python 里拆开判断
    cursor.execute("""
        SELECT name, category, price, stock, aliases
        FROM products
        WHERE aliases IS NOT NULL
    """)

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        product = row_to_product_dict(row)

        for alias in product["aliases"]:
            if alias in question:
                return product

    return None


def find_order_in_db(question):
    """
    根据用户问题，从数据库中查订单

    这里的订单号格式比较固定，例如：
    O1001、O1003

    逻辑：
    1. 先尝试从问题中提取一个类似订单号的词
    2. 再用 SQL 按订单号精确查询

    参数：
    - question：用户问题

    返回：
    - 订单字典；如果查不到，返回 None
    """

    conn = get_connection()
    cursor = conn.cursor()

    # 先把问题按空格切开，看看里面有没有像订单号的内容
    parts = question.replace("？", " ").replace("，", " ").replace("。", " ").split()

    order_id_candidate = None

    for part in parts:
        # 只做一个很简单的规则：
        # 以 O 开头，并且后面是数字
        if part.startswith("O") and part[1:].isdigit():
            order_id_candidate = part
            break

    # 如果没切出来，就再做一次宽松搜索
    if order_id_candidate is None:
        for i in range(len(question)):
            if question[i] == "O":
                j = i + 1
                digits = ""
                while j < len(question) and question[j].isdigit():
                    digits += question[j]
                    j += 1

                if digits:
                    order_id_candidate = "O" + digits
                    break

    # 如果还是没有订单号候选，直接返回 None
    if order_id_candidate is None:
        conn.close()
        return None

    # 用 SQL 精确查询
    cursor.execute("""
        SELECT
            order_id,
            product_name,
            pay_amount,
            order_status,
            logistics_company,
            tracking_number,
            shipping_status
        FROM orders
        WHERE order_id = ?
        LIMIT 1
    """, (order_id_candidate,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row_to_order_dict(row)

    return None