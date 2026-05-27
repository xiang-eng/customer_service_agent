# ================================
# workflow.py
# 作用：
# 定义整个客服 Agent 的“节点式工作流”
#
# 当前版本包含这些节点：
# 1. guard_node      安全护栏节点
# 2. intent_node     意图识别节点
# 3. planner_node    任务规划节点（支持 LLM Router）
# 4. execute_node    执行器节点
# 5. aggregate_node  聚合结果节点
# 6. general_node    问候分支节点
# 7. unknown_node    兜底分支节点
#
# 最终由 run_workflow(state) 串起来执行
# ================================

# 从规则版意图识别模块中导入函数
from intent import classify_intents

# 从 LLM 版意图识别模块中导入函数
from llm_intent import classify_intents_llm

# 从安全护栏模块中导入函数
from safety import safety_guard

# 从规则 Planner 中导入任务构造函数
# 它会把意图列表转成任务列表
from planner import build_tasks

# 从执行器模块中导入具体任务执行函数
from executors import (
    execute_price_task,
    execute_stock_task,
    execute_order_task,
    execute_policy_task,
)

# 从 LLM Router 模块中导入函数
# 它会让大模型直接判断应该走哪些任务
from llm_router import route_tasks_with_llm


# ================================
# 开关配置
# ================================

# 是否使用 LLM 做意图识别
# True  = 优先走大模型意图识别
# False = 使用规则版意图识别
USE_LLM_INTENT = False

# 是否在订单回答阶段使用 LLM 生成自然语言回复
# True  = 用 LLM 生成订单回答
# False = 用模板回答
USE_LLM_RESPONSE = True

# 是否启用 LLM Router 来直接决定任务
# True  = 优先让 LLM 决定任务
# False = 仍使用规则 Planner（build_tasks）
USE_LLM_ROUTER = True


def is_followup_question(question):
    """
    判断一句话是不是“短追问”

    为什么需要这个函数？
    因为像：
    - 那现在呢？
    - 这个呢？
    - 那物流呢？
    这种问题本身信息不完整，
    但如果结合上一轮上下文，就能理解。

    返回：
    - True：认为这是追问
    - False：认为这是一个新的独立问题
    """

    # 去掉前后空格
    q = question.strip()

    # 明确的追问表达
    explicit_followups = [
        "那现在呢",
        "现在呢",
        "然后呢",
        "这个呢",
        "那个呢",
        "还有呢",
        "那这个呢",
        "那那个呢",
        "那价格呢",
        "那库存呢",
        "那物流呢",
        "那订单呢",
        "那售后呢",
        "那退货呢",
        "那换货呢",
    ]

    # 如果和某个追问表达完全一致，就直接认为是追问
    if q in explicit_followups:
        return True

    # 如果以“那”开头，并且句子很短，也认为像追问
    # 例如：
    # “那现在呢”
    # “那物流呢”
    if q.startswith("那") and len(q) <= 8:
        return True

    # 如果以“这个/那个”开头，并且句子很短，也认为像追问
    # 例如：
    # “这个呢”
    # “那个呢”
    if (q.startswith("这个") or q.startswith("那个")) and len(q) <= 6:
        return True

    # 否则，认为不是追问
    return False


def guard_node(state):
    """
    安全检查节点

    作用：
    - 判断当前问题是否安全、是否在业务范围内
    - 如果是明确短追问，并且已有上下文，则先放行
    - 把结果写回 state
    """

    # 从 state 中取出当前问题、商品数据、会话记忆
    question = state.question
    products = state.products
    memory = state.memory

    # 判断当前问题是不是短追问
    is_short_followup = is_followup_question(question)

    # 判断当前会话里是否已经有上下文
    # 只要最近意图 / 最近商品 / 最近订单 里任意一个存在，
    # 就说明当前会话里有可参考的上下文
    has_context = (
        memory.get_last_intents() is not None
        or memory.get_last_product() is not None
        or memory.get_last_order() is not None
    )

    # 把这两个中间状态写回 state
    # 后面的意图继承节点还会用到
    state.is_short_followup = is_short_followup
    state.has_context = has_context

    # 如果不是“短追问 + 已有上下文”，就正常走安全护栏
    if not (is_short_followup and has_context):
        # 调用 safety_guard 做业务边界检查
        is_safe, guard_message = safety_guard(question, products)

        # 把安全结果写回 state
        state.is_safe = is_safe
        state.guard_message = guard_message

        # 如果不安全，就记录轨迹并标记流程停止
        if not is_safe:
            state.add_trace("【安全护栏】拦截")
            state.should_stop = True
        else:
            # 如果安全，就记录通过
            state.add_trace("【安全护栏】通过")
    else:
        # 如果是短追问，而且已经有上下文，就先放行
        state.add_trace("【安全护栏】短追问放行")
        state.is_safe = True
        state.guard_message = None

    return state


def intent_node(state):
    """
    意图识别节点

    作用：
    - 判断用户问题属于哪类意图
    - 支持规则版 / LLM版两种方案
    - 如果是短追问且当前意图不明显，尝试继承上一轮意图
    """

    # 取当前问题
    question = state.question

    # 如果开启了 LLM 意图识别，就优先使用
    if USE_LLM_INTENT:
        intents = classify_intents_llm(question)

        # 如果 LLM 调用失败，就回退到规则版
        if intents is None:
            state.add_trace("【回退】使用规则版意图识别")
            intents = classify_intents(question)
    else:
        # 默认使用规则版意图识别
        intents = classify_intents(question)

    # 如果当前被识别成 unknown_query
    # 但它又是短追问，就尝试继承上一轮意图
    if intents == ["unknown_query"]:
        if getattr(state, "is_short_followup", False):
            last_intents = state.memory.get_last_intents()

            # 如果上一轮有意图，就继承
            if last_intents is not None:
                state.add_trace("【上下文继承】当前问题意图不明显，继承上一轮意图")
                intents = last_intents

    # 把最终意图写回 state
    state.intents = intents

    # 更新会话记忆
    state.memory.update_intents(intents)

    # 记录轨迹
    state.add_trace(f"【意图识别】{state.intents}")

    return state


def planner_node(state):
    """
    任务规划节点

    当前逻辑：
    1. 优先尝试 LLM Router
    2. 如果 LLM Router 失败，再回退到规则 Planner

    最终产出：
    - state.tasks，例如：
      ["price_task", "order_task"]
    """

    # 取当前问题
    question = state.question

    # 如果开启了 LLM Router
    if USE_LLM_ROUTER:
        # 先让大模型决定应该执行哪些任务
        routed_tasks = route_tasks_with_llm(question, state.memory.response_cache)

        # 如果 LLM Router 成功返回
        if routed_tasks is not None:
            state.tasks = routed_tasks
            state.add_trace(f"【LLM Router任务】{state.tasks}")
            return state
        else:
            # 如果失败，就回退到规则 Planner
            state.add_trace("【LLM Router】失败，回退规则 Planner")

    # 规则 Planner：根据意图列表构造任务列表
    state.tasks = build_tasks(state.intents)
    state.add_trace(f"【Planner任务】{state.tasks}")

    return state


def execute_node(state):
    """
    执行节点

    作用：
    - 根据 state.tasks 调用不同执行器
    - 把执行结果追加到 state.responses
    """

    # 从 state 中取出数据
    question = state.question
    products = state.products
    orders = state.orders
    policy = state.policy
    memory = state.memory

    # 如果任务列表里有价格任务
    if "price_task" in state.tasks:
        state.add_trace("【执行器】执行价格任务")
        state.add_response(execute_price_task(question, products, memory))

    # 如果任务列表里有库存任务
    if "stock_task" in state.tasks:
        state.add_trace("【执行器】执行库存任务")
        state.add_response(execute_stock_task(question, products, memory))

    # 如果任务列表里有订单任务
    if "order_task" in state.tasks:
        state.add_trace("【执行器】执行订单任务")
        state.add_response(execute_order_task(question, orders, memory, USE_LLM_RESPONSE))

    # 如果任务列表里有售后任务
    if "policy_task" in state.tasks:
        state.add_trace("【执行器】执行售后任务")
        state.add_response(execute_policy_task(question, policy))

    return state


def aggregate_node(state):
    """
    聚合节点

    作用：
    - 把 state.responses 里的多段回答拼接成最终回复
    """

    state.final_response = state.get_final_response()
    return state


def general_node(state):
    """
    问候分支节点

    作用：
    - 处理 general_query
    """

    state.add_trace("【分支】进入问候节点")
    state.final_response = "您好，我是智能客服助手，请问有什么可以帮您？"
    return state


def unknown_node(state):
    """
    兜底分支节点

    作用：
    - 处理 unknown_query
    """

    state.add_trace("【分支】进入兜底节点")
    state.final_response = "抱歉，我暂时没有理解您的问题。您可以问我商品价格、库存、订单或售后政策。"
    return state


def run_workflow(state):
    """
    运行完整工作流

    执行顺序：
    1. 安全检查节点
    2. 意图识别节点
    3. 根据意图选择分支
       - general_query → 问候分支
       - unknown_query → 兜底分支
       - 其他业务意图 → 业务执行分支
    4. 对业务问题继续执行：
       planner → execute → aggregate
    """

    # 每次运行前，初始化控制状态
    state.should_stop = False
    state.final_response = None

    # =========================
    # 1. 安全检查
    # =========================
    state = guard_node(state)

    # 如果安全护栏要求停止，就直接返回
    if getattr(state, "should_stop", False):
        state.final_response = state.guard_message
        return state

    # =========================
    # 2. 意图识别
    # =========================
    state = intent_node(state)

    # =========================
    # 3. 分支判断
    # =========================

    # 如果只是普通问候
    if state.intents == ["general_query"]:
        return general_node(state)

    # 如果是不理解的问题
    if state.intents == ["unknown_query"]:
        return unknown_node(state)

    # 否则进入正常业务执行分支
    state.add_trace("【分支】进入业务执行分支")

    # =========================
    # 4. 正常业务执行
    # =========================
    state = planner_node(state)
    state = execute_node(state)
    state = aggregate_node(state)

    return state