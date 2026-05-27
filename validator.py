def validate_order_response(response_text, order):
    """
    校验订单回答是否包含关键字段

    参数：
    - response_text: LLM 生成的回答文本
    - order: 当前订单对象（字典）

    返回：
    - True  = 校验通过，可以用这条回答
    - False = 校验失败，应回退到模板回答
    """

    if response_text is None:
        return False

    # 从真实订单数据里取关键字段
    required_fields = [
        str(order["order_id"]),
        str(order["product_name"]),
        str(order["tracking_number"]),
        str(order["shipping_status"]),
    ]

    # 统计命中了多少个关键字段
    hit_count = 0

    for field in required_fields:
        if field in response_text:
            hit_count += 1

    # 至少命中 3 个关键字段才算通过
    # 你也可以以后改得更严格
    if hit_count >= 3:
        return True

    return False