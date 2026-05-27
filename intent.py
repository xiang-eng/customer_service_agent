def classify_intents(question):
    """
    判断用户问题可能包含哪些意图，返回意图列表

    返回值示例：
    ["price_query"]
    ["stock_query", "policy_query"]
    """

    intents = []

    # =========================
    # 1. 价格查询
    # =========================
    # 只要问题里出现这些词，就认为用户在问价格
    if any(word in question for word in [
        "多少钱", "价格", "售价", "贵不贵", "贵吗"
    ]):
        intents.append("price_query")

    # =========================
    # 2. 库存查询
    # =========================
    if any(word in question for word in [
        "库存", "有货", "还有货", "缺货", "有没有", "有没有货"
    ]):
        intents.append("stock_query")

    # =========================
    # 3. 售后 / 退换 / 保修
    # =========================
    # 这里重点补充更自然的口语表达
    if any(word in question for word in [
        "退货", "换货", "售后", "保修", "质量问题", "无理由",
        "能退吗", "可以退吗", "能换吗", "可以换吗",
        "坏了", "坏了咋办", "坏了怎么办",
        "能不能退", "能不能退货", "能不能换", "能不能换货",
        "这个商品能不能退", "这个商品能不能换"
    ]):
        intents.append("policy_query")

    # =========================
    # 4. 订单 / 物流
    # =========================
    if any(word in question for word in [
        "订单", "物流", "快递", "发货", "签收", "到哪了", "在哪", "到哪"
    ]):
        intents.append("order_query")

    # =========================
    # 5. 问候
    # =========================
    # 只有前面没识别出业务意图时，才把它算作普通问候
    if not intents and any(word in question for word in ["你好", "您好", "在吗"]):
        intents.append("general_query")

    # =========================
    # 6. 兜底
    # =========================
    if not intents:
        intents.append("unknown_query")

    return intents