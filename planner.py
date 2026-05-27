def build_tasks(intents):
    """
    根据识别出来的意图，构造任务列表

    例如：
    ["price_query", "stock_query", "policy_query"]
    变成：
    ["price_task", "stock_task", "policy_task"]
    """

    tasks = []

    if "price_query" in intents:
        tasks.append("price_task")

    if "stock_query" in intents:
        tasks.append("stock_task")

    if "order_query" in intents:
        tasks.append("order_task")

    if "policy_query" in intents:
        tasks.append("policy_task")

    if "general_query" in intents:
        tasks.append("general_task")

    if "unknown_query" in intents:
        tasks.append("unknown_task")

    return tasks