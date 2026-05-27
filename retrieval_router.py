from executors import (
    execute_price_task,
    execute_stock_task,
    execute_order_task,
    execute_policy_task,
)


def get_product_name_from_memory(memory):
    """
    从 memory 里取最近商品名。

    优先级：
    1. last_order 里的 product_name
    2. last_order 里的 product
    3. last_product 里的 product_name
    4. last_product 里的 name
    """

    last_order = memory.get_last_order()

    if last_order:
        product_name = (
            last_order.get("product_name")
            or last_order.get("product")
        )

        if product_name:
            return product_name

    last_product = memory.get_last_product()

    if last_product:
        product_name = (
            last_product.get("product_name")
            or last_product.get("name")
        )

        if product_name:
            return product_name

    return None


def route_and_retrieve(
    question,
    tasks,
    products,
    orders,
    policy,
    memory,
    use_llm_response=True
):
    """
    根据任务列表动态调用工具。

    返回：
    - final_answer
    - evidence
    """

    responses = []
    evidence = []

    if "price_task" in tasks:
        print("【RetrievalRouter】调用价格工具")

        result = execute_price_task(
            question,
            products,
            memory
        )

        responses.append(result)

        evidence.append(
            {
                "source": "product_db",
                "task": "price_task",
                "content": result
            }
        )

    if "stock_task" in tasks:
        print("【RetrievalRouter】调用库存工具")

        result = execute_stock_task(
            question,
            products,
            memory
        )

        responses.append(result)

        evidence.append(
            {
                "source": "product_db",
                "task": "stock_task",
                "content": result
            }
        )

    if "order_task" in tasks:
        print("【RetrievalRouter】调用订单工具")

        result = execute_order_task(
            question,
            orders,
            memory,
            use_llm_response=use_llm_response
        )

        responses.append(result)

        evidence.append(
            {
                "source": "order_db",
                "task": "order_task",
                "content": result
            }
        )

    if "policy_task" in tasks:
        print("【RetrievalRouter】调用售后 RAG 工具")

        product_name = get_product_name_from_memory(memory)

        if product_name and product_name not in question:
            policy_question = f"{product_name} {question}"
        else:
            policy_question = question

        print(f"【RetrievalRouter】售后检索问题：{policy_question}")

        result = execute_policy_task(
            policy_question,
            policy
        )

        responses.append(result)

        evidence.append(
            {
                "source": "policy_rag",
                "task": "policy_task",
                "content": result
            }
        )

    cleaned = []

    for response in responses:
        if response is None:
            continue

        response = response.strip()

        if not response:
            continue

        if response not in cleaned:
            cleaned.append(response)

    final_answer = "\n".join(cleaned)

    return final_answer, evidence