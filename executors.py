# =====================================
# executors.py
# 作用：
# 工具执行器
#
# 负责执行具体任务：
# - execute_price_task  查价格
# - execute_stock_task  查库存
# - execute_order_task  查订单
# - execute_policy_task 查售后政策
#
# 当前版本特点：
# 1. 商品 / 订单优先从传入的数据列表中查
# 2. 查不到再回退到数据库查询函数
# 3. 订单回答优先使用 Qwen / DeepSeek 生成自然语言
# 4. LLM 不可用时自动回退模板，不影响系统运行
# 5. 售后 RAG 出错时自动回退本地售后规则
# =====================================

from db_tools import find_order_in_db, find_product_in_db

from llm_response import generate_response_with_llm



def format_number(value):
    """
    格式化数字。

    例如：
    - 199.0 -> 199
    - 199   -> 199
    - 199.5 -> 199.5
    """

    if isinstance(value, float):
        if value.is_integer():
            return int(value)

    return value


def find_product_from_list(question, products):
    """
    优先从传入的 products 列表中查商品。

    这样 Streamlit Demo 和测试脚本中的商品数据可以直接生效。
    """

    if not products:
        return None

    for product in products:
        names = [
            product.get("id"),
            product.get("name"),
            product.get("product_name"),
            product.get("brand"),
        ]

        aliases = product.get("aliases", [])

        names.extend(aliases)

        for name in names:
            if name and str(name) in question:
                return product

    return None


def find_order_from_list(question, orders):
    """
    优先从传入的 orders 列表中查订单。
    """

    if not orders:
        return None

    for order in orders:
        order_id = order.get("order_id")

        if order_id and str(order_id) in question:
            return order

    return None


def get_product_name(product):
    """
    获取商品名，兼容 name / product_name。
    """

    return (
        product.get("name")
        or product.get("product_name")
        or "未知商品"
    )


def get_order_value(order, *keys, default="未知"):
    """
    从订单字典中取值，兼容多个字段名。

    例如：
    - order_status / status
    - pay_amount / amount
    - tracking_number / tracking_no / tracking
    """

    for key in keys:
        if key in order and order[key] is not None:
            return order[key]

    return default


def safe_update_product(memory, product):
    """
    安全更新商品记忆。

    如果 memory 里没有 update_product，也不会报错。
    """

    try:
        if hasattr(memory, "update_product"):
            memory.update_product(product)
    except Exception:
        pass


def safe_update_order(memory, order):
    """
    安全更新订单记忆。

    同时把订单里的商品同步到 last_product，
    避免“订单里的商品可以退货吗”之后追问“那退货呢”时上下文错乱。
    """

    try:
        if hasattr(memory, "update_order"):
            memory.update_order(order)
    except Exception:
        pass

    product_name = (
        order.get("product_name")
        or order.get("product")
    )

    if product_name:
        safe_update_product(
            memory,
            {
                "name": product_name,
                "product_name": product_name
            }
        )


def execute_price_task(question, products, memory):
    """
    执行价格任务。

    参数：
    - question：用户问题
    - products：商品数据列表
    - memory：会话记忆对象

    返回：
    - 商品价格回答
    """

    product = find_product_from_list(question, products)

    if product is None:
        product = find_product_in_db(question)

    if product is not None:
        safe_update_product(memory, product)
    else:
        if hasattr(memory, "get_last_product"):
            product = memory.get_last_product()

    if product is None:
        return "请问您想查询哪一款商品的价格？"

    name = get_product_name(product)

    price = product.get("price")

    if price is None:
        return f"{name} 暂时没有价格信息。"

    price = format_number(price)

    return f"{name} 的价格是 {price} 元。"


def execute_stock_task(question, products, memory):
    """
    执行库存任务。

    参数：
    - question：用户问题
    - products：商品数据列表
    - memory：会话记忆对象

    返回：
    - 商品库存回答
    """

    product = find_product_from_list(question, products)

    if product is None:
        product = find_product_in_db(question)

    if product is not None:
        safe_update_product(memory, product)
    else:
        if hasattr(memory, "get_last_product"):
            product = memory.get_last_product()

    if product is None:
        return "请问您想查询哪一款商品的库存？"

    name = get_product_name(product)

    stock = product.get("stock")

    if stock is None:
        return f"{name} 暂时没有库存信息。"

    return f"{name} 当前库存为 {stock} 件。"


def execute_order_task(question, orders, memory, use_llm_response=True):
    """
    执行订单任务。

    当前逻辑：

    1. 先查订单
    2. 更新 memory 中的 last_order 和 last_product
    3. 整理订单事实 tool_result
    4. 如果开启 LLM，则调用 Qwen / DeepSeek 生成自然语言回答
    5. 如果 LLM 成功，直接返回 LLM 回答
    6. 如果 LLM 失败，回退模板回答
    """

    order = find_order_from_list(question, orders)

    if order is None:
        order = find_order_in_db(question)

    if order is not None:
        safe_update_order(memory, order)
    else:
        if hasattr(memory, "get_last_order"):
            order = memory.get_last_order()

    if order is None:
        return "请提供订单号，例如 O1001，我可以帮您查询订单状态。"

    order_id = get_order_value(
        order,
        "order_id"
    )

    order_status = get_order_value(
        order,
        "order_status",
        "status"
    )

    product_name = get_order_value(
        order,
        "product_name",
        "product"
    )

    pay_amount = get_order_value(
        order,
        "pay_amount",
        "amount",
        default=0
    )

    logistics_company = get_order_value(
        order,
        "logistics_company",
        default="暂无"
    )

    tracking_number = get_order_value(
        order,
        "tracking_number",
        "tracking_no",
        "tracking",
        default="暂无运单"
    )

    shipping_status = get_order_value(
        order,
        "shipping_status",
        "logistics_status",
        default="暂无物流状态"
    )

    pay_amount = format_number(pay_amount)

    tool_result = (
        f"订单号：{order_id}\n"
        f"订单状态：{order_status}\n"
        f"商品：{product_name}\n"
        f"支付金额：{pay_amount} 元\n"
        f"物流公司：{logistics_company}\n"
        f"物流单号：{tracking_number}\n"
        f"物流状态：{shipping_status}"
    )

    if use_llm_response:
        llm_response = generate_response_with_llm(
            question=question,
            tool_result=tool_result,
            response_cache=memory.response_cache,
            task_type="order_task"
        )

        if llm_response is not None and llm_response.strip():
            print("【订单回答】LLM 生成成功，返回自然语言回答")
            return llm_response

        print("【订单回答】LLM 不可用，回退模板回答")

    return (
        f"订单 {order_id} 当前状态为：{order_status}。\n"
        f"商品：{product_name}，支付金额：{pay_amount} 元。\n"
        f"物流公司：{logistics_company}，物流单号：{tracking_number}。\n"
        f"物流状态：{shipping_status}。"
    )


def fallback_policy_answer(question):
    """
    售后 RAG 失败时的兜底回答。

    避免 Chroma / RAG / LLM 出错导致页面崩溃。
    """

    if "退货" in question or "退款" in question:
        return (
            "根据售后政策：\n"
            "1. 未拆封商品支持 7 天无理由退货。\n"
            "2. 已拆封但无质量问题的商品，不支持无理由退货。\n"
            "3. 如果商品存在质量问题，可以申请售后处理。\n"
            "4. 退款会在退货商品入库并检测通过后 3-7 个工作日原路退回。"
        )

    if "换货" in question:
        return (
            "根据售后政策：\n"
            "如果商品存在质量问题，支持 15 天内换货。"
        )

    if "保修" in question or "维修" in question:
        return (
            "根据售后政策：\n"
            "保修期内非人为损坏，可以申请维修。"
        )

    return (
        "根据售后政策：\n"
        "未拆封商品支持 7 天无理由退货；"
        "已拆封但无质量问题的商品，不支持无理由退货；"
        "质量问题支持 15 天内换货；"
        "保修期内非人为损坏可申请维修。"
    )


def execute_policy_task(question, policy):
    """
    执行售后任务。

    优先使用完整版 RAG。
    如果 Chroma / LLM / 数据库出错，则回退到本地售后规则回答。
    """

    try:
        from full_rag_policy import answer_policy_with_full_rag

        answer = answer_policy_with_full_rag(
            question,
            top_k=3
        )

        if answer is not None and answer.strip():
            return answer

        return fallback_policy_answer(question)

    except Exception as e:
        print(f"【售后RAG失败，启用兜底回答】{e}")
        return fallback_policy_answer(question)
