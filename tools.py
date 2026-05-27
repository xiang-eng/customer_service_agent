#根据问题去不同数据源查东西

def find_product(question, products):#find_product → 查商品
    """根据用户问题查找商品"""

    for product in products:
        if product["name"] in question:
            return product

        for alias in product["aliases"]:
            if alias in question:
                return product

    return None


def find_order(question, orders):#find_order → 查订单
    """根据用户问题查找订单"""

    for order in orders:
        if order["order_id"] in question:
            return order

    return None


def search_policy(question, policy):#search_policy → 查售后政策
    """根据用户问题，从售后政策中检索相关内容"""

    lines = policy.splitlines()
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

    return "\n".join(matched_lines)