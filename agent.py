from intent import classify_intents
from llm_intent import classify_intents_llm
from safety import safety_guard
from planner import build_tasks
from executors import (
    execute_price_task,
    execute_stock_task,
    execute_order_task,
    execute_policy_task,
)


USE_LLM_INTENT = False
USE_LLM_RESPONSE = True


def answer_question(state):
    """
    根据用户问题生成回答
    改成围绕 state 对象流转，更接近 Agent / LangGraph 风格
    """

    question = state.question
    products = state.products
    orders = state.orders
    policy = state.policy
    memory = state.memory

    # =========================
    # 一、先判断是不是“短追问”
    # =========================
    short_followup_markers = ["那", "那现在", "现在呢", "然后呢", "呢", "这个呢", "那个呢"]

    is_short_followup = (
        len(question) <= 8 or any(marker in question for marker in short_followup_markers)
    )

    has_context = (
        memory.get_last_intents() is not None
        or memory.get_last_product() is not None
        or memory.get_last_order() is not None
    )

    # =========================
    # 二、安全检查
    # =========================
    if not (is_short_followup and has_context):
        is_safe, guard_message = safety_guard(question, products)
        if not is_safe:
            state.add_trace("【安全护栏】拦截")
            return guard_message
        else:
            state.add_trace("【安全护栏】通过")
    else:
        state.add_trace("【安全护栏】短追问放行")

    # =========================
    # 三、意图识别
    # =========================
    if USE_LLM_INTENT:
        intents = classify_intents_llm(question)
        if intents is None:
            state.add_trace("【回退】使用规则版意图识别")
            intents = classify_intents(question)
    else:
        intents = classify_intents(question)

    # =========================
    # 四、上下文意图继承
    # =========================
    if intents == ["unknown_query"]:
        if is_short_followup:
            last_intents = memory.get_last_intents()
            if last_intents is not None:
                state.add_trace("【上下文继承】当前问题意图不明显，继承上一轮意图")
                intents = last_intents

    state.intents = intents
    state.add_trace(f"【意图识别】{state.intents}")

    memory.update_intents(intents)

    # =========================
    # 五、Planner 生成任务
    # =========================
    state.tasks = build_tasks(intents)
    state.add_trace(f"【Planner任务】{state.tasks}")

    # =========================
    # 六、特殊情况
    # =========================
    if intents == ["unknown_query"]:
        return "抱歉，我暂时没有理解您的问题。您可以问我商品价格、库存、订单或售后政策。"

    if intents == ["general_query"]:
        return "您好，我是智能客服助手，请问有什么可以帮您？"

    # =========================
    # 七、执行任务
    # =========================
    if "price_task" in state.tasks:
        state.add_trace("【执行器】执行价格任务")
        state.add_response(execute_price_task(question, products, memory))

    if "stock_task" in state.tasks:
        state.add_trace("【执行器】执行库存任务")
        state.add_response(execute_stock_task(question, products, memory))

    if "order_task" in state.tasks:
        state.add_trace("【执行器】执行订单任务")
        state.add_response(execute_order_task(question, orders, memory, USE_LLM_RESPONSE))

    if "policy_task" in state.tasks:
        state.add_trace("【执行器】执行售后任务")
        state.add_response(execute_policy_task(question, policy))

    # =========================
    # 八、聚合结果
    # =========================
    return state.get_final_response()