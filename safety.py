def safety_guard(question, products):
    """
    安全护栏：判断用户问题是否在业务范围内

    返回：
    - True, "通过"   表示允许进入后续主流程
    - False, "提示语" 表示直接拦截
    """

    # =========================
    # 1. 隐私类问题：直接拒绝
    # =========================
    privacy_keywords = ["手机号", "身份证", "密码", "银行卡", "住址", "家庭地址", "隐私"]

    # 如果用户问题里出现隐私关键词，就直接拒绝
    if any(word in question for word in privacy_keywords):
        return False, "抱歉，涉及隐私信息的问题我无法处理。"

    # =========================
    # 2. 违法/高风险问题：直接拒绝
    # =========================
    illegal_keywords = ["违法", "赌博", "枪", "毒品", "黑客", "破解", "攻击"]

    if any(word in question for word in illegal_keywords):
        return False, "抱歉，这类问题超出了客服系统的服务范围，我无法处理。"

    # =========================
    # 3. 问候语：允许通过
    # =========================
    greeting_keywords = ["你好", "您好", "在吗"]

    if any(word in question for word in greeting_keywords):
        return True, "通过"

    # =========================
    # 4. 订单 / 售后类问题：允许通过
    # =========================
    # 这里专门补充口语表达，让更自然的说法也能放行
    service_keywords = [
        # 订单 / 物流
        "订单", "物流", "快递", "发货", "签收", "到哪了", "在哪", "到哪",

        # 售后 / 退换 / 保修
        "退货", "换货", "售后", "保修", "质量问题", "无理由",

        # 口语表达
        "能退吗", "可以退吗", "能不能退", "能不能退货",
        "能换吗", "可以换吗", "能不能换", "能不能换货",
        "坏了", "坏了咋办", "坏了怎么办"
    ]

    if any(word in question for word in service_keywords):
        return True, "通过"

    # =========================
    # 5. 商品名 / 类别 / 别名：允许通过
    # =========================
    for product in products:
        # 商品全名
        if product["name"] in question:
            return True, "通过"

        # 商品类别
        if product["category"] in question:
            return True, "通过"

        # 商品别名
        for alias in product["aliases"]:
            if alias in question:
                return True, "通过"

    # =========================
    # 6. 商品相关问题但没提具体商品：也允许通过
    # =========================
    # 这样后面主流程可以继续问用户：
    # “请问您想查询哪一款商品的价格？”
    shopping_keywords = [
        "多少钱", "价格", "售价", "贵吗", "贵不贵",
        "库存", "有货", "还有货", "有没有货",
        "这个商品", "这个", "那个商品", "那个"
    ]

    if any(word in question for word in shopping_keywords):
        return True, "通过"

    # =========================
    # 7. 其他无关问题：拒绝
    # =========================
    return False, "抱歉，我目前只能处理智能家居商品、订单物流和售后政策相关问题。"