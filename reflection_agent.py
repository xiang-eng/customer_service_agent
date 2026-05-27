# =====================================
# reflection_agent.py
# Agentic RAG 反思检查模块增强版
# =====================================


def evidence_enough(answer, evidence):
    """
    判断当前回答是否足够可信。
    """

    if answer is None:
        return False

    answer = answer.strip()

    if not answer:
        return False

    if not evidence:
        return False

    bad_signals = [
        "抱歉，我暂时没有找到相关信息",
        "抱歉没有理解问题",
        "请问您想查询哪一款商品",
        "请提供订单号",
        "暂时没有找到明确政策",
        "没有找到相关",
    ]

    for signal in bad_signals:
        if signal in answer:
            return False

    # 如果回答太短，认为不够
    if len(answer) < 8:
        return False

    # 至少有一个有效证据内容
    valid_evidence_count = 0

    for item in evidence:
        content = item.get("content", "")

        if content and len(content.strip()) >= 5:
            valid_evidence_count += 1

    if valid_evidence_count == 0:
        return False

    return True


def reflect_and_replan(question, previous_tasks, attempt):
    """
    当回答不够好时，重新规划任务。
    """

    print(f"【ReflectionAgent】第 {attempt} 轮回答不充分，开始重新规划")

    new_tasks = list(previous_tasks)

    policy_keywords = [
        "退货",
        "换货",
        "售后",
        "保修",
        "维修",
        "质量问题",
        "发票",
        "退款",
    ]

    order_keywords = [
        "订单",
        "物流",
        "快递",
        "配送",
        "收货",
        "运单",
    ]

    price_keywords = [
        "价格",
        "多少钱",
        "售价",
        "贵不贵",
    ]

    stock_keywords = [
        "库存",
        "有货",
        "现货",
        "缺货",
    ]

    if any(word in question for word in policy_keywords):
        if "policy_task" not in new_tasks:
            print("【ReflectionAgent】补充 policy_task")
            new_tasks.append("policy_task")

    if any(word in question for word in order_keywords):
        if "order_task" not in new_tasks:
            print("【ReflectionAgent】补充 order_task")
            new_tasks.append("order_task")

    if any(word in question for word in price_keywords):
        if "price_task" not in new_tasks:
            print("【ReflectionAgent】补充 price_task")
            new_tasks.append("price_task")

    if any(word in question for word in stock_keywords):
        if "stock_task" not in new_tasks:
            print("【ReflectionAgent】补充 stock_task")
            new_tasks.append("stock_task")

    return new_tasks