import csv
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_FILE = os.path.join(BASE_DIR, "data", "products.csv")
POLICY_FILE = os.path.join(BASE_DIR, "data", "policy.txt")
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

def classify_intent(question):#用户意图函数
    """判断用户问题属于哪一类"""

    if any(word in question for word in ["多少钱", "价格", "售价", "贵不贵"]):
        return "price_query"

    if any(word in question for word in ["库存", "有货", "还有货", "缺货"]):
        return "stock_query"

    if any(word in question for word in ["退货", "换货", "售后", "保修", "质量问题"]):
        return "policy_query"

    if any(word in question for word in ["你好", "您好", "在吗"]):
        return "general_query"

    return "unknown_query"


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


def answer_question(question, products, policy):#回答问题函数
    """根据用户问题生成回答"""

    intent = classify_intent(question)

    if intent == "general_query":
        return "您好，我是智能客服助手，请问有什么可以帮您？"

    if intent == "price_query":
        product = find_product(question, products)

        if product is None:
            return "请问您想查询哪一款商品的价格？"
      #变量 = A if 条件 else B
      #如果 条件 成立，就把 A 赋值给变量，否则，就把 B 赋值给变量
      #product["price"].is_integer()，这是判断一个小数是不是“整数形式”


        price = int(product["price"]) if product["price"].is_integer() else product["price"]
        return f"{product['name']} 的价格是 {price} 元。"

    if intent == "stock_query":
        product = find_product(question, products)

        if product is None:
            return "请问您想查询哪一款商品的库存？"

        return f"{product['name']} 当前库存为 {product['stock']} 件。"

    if intent == "policy_query":
        matched_policy = search_policy(question, policy)
        return f"根据我们的售后政策：\n{matched_policy}"

    return "抱歉，我暂时没有理解您的问题。您可以问我商品价格、库存或售后政策。"


def main():
    products = load_products()
    policy = load_policy()

    print("智能客服系统已启动。")
    print("你可以问：小米智能音箱多少钱？")
    print("输入 exit 退出系统。")
    print("-" * 40)

    while True:
        question = input("用户：")

        if question.lower() in ["exit", "quit", "退出"]:
            print("客服：感谢使用，再见！")
            break

        response = answer_question(question, products, policy)
        print("客服：" + response)#打印出来的是 客服：您好
        print("-" * 40)


if __name__ == "__main__":
    main()