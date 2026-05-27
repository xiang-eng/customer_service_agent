# =====================================
# planner_agentic.py
# 作用：
# Agentic RAG 的增强任务规划器
#
# 普通 Planner：
# 用户问什么，就生成一个任务
#
# Agentic Planner：
# 会处理多跳问题，自动补充多个任务
# =====================================

from planner import build_tasks


def build_agentic_tasks(question, intents):
    """
    根据用户问题和意图，生成任务列表。

    参数：
    - question：用户问题
    - intents：意图列表

    返回：
    - tasks：任务列表
    """

    # 先复用你原来的规则 Planner
    tasks = build_tasks(intents)

    # ==========================
    # 多跳问题增强
    # ==========================
    # 例如：
    # 用户问：我的订单 O1001 里的商品可以退货吗？
    #
    # 这个问题其实需要：
    # 1. 查订单
    # 2. 查售后政策
    #
    # 所以要同时加入 order_task 和 policy_task
    # ==========================

    order_words = [
        "订单",
        "物流",
        "快递",
        "配送",
        "收货",
        "运单"
    ]

    policy_words = [
        "退货",
        "换货",
        "售后",
        "保修",
        "维修",
        "退款",
        "质量问题"
    ]

    price_words = [
        "价格",
        "多少钱",
        "售价"
    ]

    stock_words = [
        "库存",
        "有货",
        "现货"
    ]

    # 如果问题里出现订单相关词
    if any(word in question for word in order_words):
        if "order_task" not in tasks:
            tasks.append("order_task")

    # 如果问题里出现售后相关词
    if any(word in question for word in policy_words):
        if "policy_task" not in tasks:
            tasks.append("policy_task")

    # 如果问题里出现价格相关词
    if any(word in question for word in price_words):
        if "price_task" not in tasks:
            tasks.append("price_task")

    # 如果问题里出现库存相关词
    if any(word in question for word in stock_words):
        if "stock_task" not in tasks:
            tasks.append("stock_task")

    # ==========================
    # 典型多跳句式
    # ==========================
    # 例如：
    # 我的订单里的商品能不能退货？
    # 既有订单，又有售后
    # ==========================

    if "订单" in question and any(word in question for word in policy_words):

        if "order_task" not in tasks:
            tasks.append("order_task")

        if "policy_task" not in tasks:
            tasks.append("policy_task")

    return tasks