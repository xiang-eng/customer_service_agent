'''
用户提问
  ↓
安全护栏 safety_guard()
  ↓
多意图识别 classify_intents()
  ↓
商品查询 find_product()
  ↓
订单查询 find_order()
  ↓
政策检索 search_policy()
  ↓
合并回答 answer_question()
'''
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_FILE = os.path.join(BASE_DIR, "data", "products.csv")
POLICY_FILE = os.path.join(BASE_DIR, "data", "policy.txt")
ORDER_FILE = os.path.join(BASE_DIR, "data", "orders.csv")
'''
# 获取当前这个 Python 文件所在的文件夹路径
# __file__ 表示当前 Python 文件
# os.path.abspath(__file__) 表示获取当前文件的绝对路径
# os.path.dirname(...) 表示获取这个文件所在的文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 拼接商品数据文件的完整路径
# 相当于：当前项目文件夹 / data / products.csv
PRODUCT_FILE = os.path.join(BASE_DIR, "data", "products.csv")

# 拼接售后政策文件的完整路径
# 相当于：当前项目文件夹 / data / policy.txt
POLICY_FILE = os.path.join(BASE_DIR, "data", "policy.txt")
'''
def load_products():
    """读取商品 CSV 数据"""
    products = []

    with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["price"] = float(row["price"])#csv读出来的都是字符串
            row["stock"] = int(row["stock"])#csv读出来的都是字符串
            row["aliases"] = row["aliases"].split("|")#把别名字符串切成列表。
            products.append(row)

    return products
def load_orders():#读取订单函数
    """读取订单 CSV 数据"""
    orders = []

    with open(ORDER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["pay_amount"] = float(row["pay_amount"])#把订单支付金额从字符串转成小数。
            orders.append(row)

    return orders

def load_policy():
    """读取售后政策文本"""
    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return f.read()
def search_policy(question, policy):
    """根据用户问题，从售后政策中检索相关内容"""

    lines = policy.splitlines()#把完整的售后政策文本，按行拆成列表。
    matched_lines = []

    if "退货" in question:
        keywords = ["退货", "无理由"]
    elif "换货" in question or "质量问题" in question:
        keywords = ["换货", "质量问题"]
    elif "保修" in question:
        keywords = ["保修"]
    else:
        keywords = ["退货", "换货", "保修", "质量问题"]

    for line in lines:
        for keyword in keywords:
            if keyword in line:
                matched_lines.append(line)
                break

    if not matched_lines:
        return "暂时没有找到相关售后政策，请联系人工客服确认。"

    return "\n".join(matched_lines)#把找到的多行政策，用换行符拼接成一个字符串。
def safety_guard(question, products):
    """安全护栏：判断用户问题是否在业务范围内"""

    # 1. 隐私类问题，直接拒绝
    privacy_keywords = ["手机号", "身份证", "密码", "银行卡", "住址", "家庭地址", "隐私"]

    if any(word in question for word in privacy_keywords):
        return False, "抱歉，涉及隐私信息的问题我无法处理。"

    # 2. 违法或高风险问题，直接拒绝
    illegal_keywords = ["违法", "赌博", "枪", "毒品", "黑客", "破解", "攻击"]

    if any(word in question for word in illegal_keywords):
        return False, "抱歉，这类问题超出了客服系统的服务范围，我无法处理。"

    # 3. 问候语允许通过
    greeting_keywords = ["你好", "您好", "在吗"]

    if any(word in question for word in greeting_keywords):
        return True, "通过"

    # 4. 订单、物流、售后类问题允许通过
    service_keywords = [
        "订单", "物流", "快递", "发货", "签收", "到哪了",
        "退货", "换货", "售后", "保修", "质量问题", "无理由"
    ]

    if any(word in question for word in service_keywords):
        return True, "通过"

    # 5. 商品库里的商品允许通过
    for product in products:
        if product["name"] in question:
            return True, "通过"

        if product["category"] in question:
            return True, "通过"

        for alias in product["aliases"]:
            if alias in question:
                return True, "通过"

    # 6. 明显问了不支持的商品，拒绝
    shopping_keywords = ["多少钱", "价格", "库存", "有货", "还有货", "售价"]

    if any(word in question for word in shopping_keywords):
        return False, "抱歉，我们目前主要经营智能家居类商品，暂不支持该类商品查询。"

    # 7. 其他无关问题，拒绝
    return False, "抱歉，我目前只能处理智能家居商品、订单物流和售后政策相关问题。"
def classify_intents(question):
    """判断用户问题可能包含哪些意图，返回意图列表"""

    intents = []

    if any(word in question for word in ["多少钱", "价格", "售价", "贵不贵"]):
        intents.append("price_query")

    if any(word in question for word in ["库存", "有货", "还有货", "缺货"]):
        intents.append("stock_query")

    if any(word in question for word in ["退货", "换货", "售后", "保修", "质量问题", "无理由"]):
        intents.append("policy_query")

    if any(word in question for word in ["订单", "物流", "快递", "发货", "签收", "到哪了"]):
        intents.append("order_query")

    if not intents and any(word in question for word in ["你好", "您好", "在吗"]):
        intents.append("general_query")

    if not intents:
        intents.append("unknown_query")

    return intents
def find_product(question, products):#查找商品函数
    """根据用户问题查找商品"""

    for product in products:
        # 先匹配完整商品名
        if product["name"] in question:
            return product

        # 再匹配别名
        for alias in product["aliases"]:
            if alias in question:
                return product

    return None
def find_order(question, orders):#查找订单函数
    """根据用户问题查找订单"""

    for order in orders:
        if order["order_id"] in question:
            return order

    return None

def answer_question(question, products, orders, policy):
    """根据用户问题生成回答，支持复合问题"""

    is_safe, guard_message = safety_guard(question, products)

    if not is_safe:
        return guard_message

    intents = classify_intents(question)
    responses = []

    # 只是不认识的问题
    if intents == ["unknown_query"]:
        return "抱歉，我暂时没有理解您的问题。您可以问我商品价格、库存或售后政策。"

    # 只是普通问候
    if intents == ["general_query"]:
        return "您好，我是智能客服助手，请问有什么可以帮您？"

    # 根据用户问题，查找用户问的是哪个商品。
    product = find_product(question, products)

    if "price_query" in intents:
        if product is None:
            responses.append("请问您想查询哪一款商品的价格？")
        else:
            price = int(product["price"]) if product["price"].is_integer() else product["price"]
            responses.append(f"{product['name']} 的价格是 {price} 元。")

    if "stock_query" in intents:
        if product is None:
            responses.append("请问您想查询哪一款商品的库存？")
        else:
            responses.append(f"{product['name']} 当前库存为 {product['stock']} 件。")

    if "order_query" in intents:
        order = find_order(question, orders)

        if order is None:
            responses.append("请提供订单号，例如 O1001，我可以帮您查询订单状态。")
        else:
            pay_amount = int(order["pay_amount"]) if order["pay_amount"].is_integer() else order["pay_amount"]

            responses.append(
                f"订单 {order['order_id']} 当前状态为：{order['order_status']}。\n"
                f"商品：{order['product_name']}，支付金额：{pay_amount} 元。\n"
                f"物流公司：{order['logistics_company']}，物流单号：{order['tracking_number']}。\n"
                f"物流状态：{order['shipping_status']}。"
            )  
    if "policy_query" in intents:
        matched_policy = search_policy(question, policy)
        responses.append(f"根据我们的售后政策：\n{matched_policy}")   
               
    return "\n".join(responses)#把 responses 里面的多条回答，用换行连接成一个字符串。


def main():
    products = load_products()
    orders = load_orders()
    policy = load_policy()
#把 data 文件夹里的数据读进程序
    print("智能客服系统已启动。")
    print("你可以问：小米智能音箱多少钱？")
    print("输入 exit 退出系统。")
    print("-" * 40)

    while True:
        question = input("用户：")

        if question.lower() in ["exit", "quit", "退出"]:
            print("客服：感谢使用，再见！")
            break

        response = answer_question(question, products, orders, policy)
        print("客服：" + response)#打印出来的是 客服：您好
        print("-" * 40)


if __name__ == "__main__":
    main()

