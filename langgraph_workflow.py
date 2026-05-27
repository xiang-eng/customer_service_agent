# ================================
# langgraph_workflow.py
# 作用：
# 用 LangGraph 重写当前客服系统的核心工作流
#
# 当前版本是“最小 LangGraph 版”：
# - guard_node
# - intent_node
# - planner_node
# - execute_node
# - aggregate_node
#
# 同时保留：
# - general 分支
# - unknown 分支
# - 安全拦截分支
#
# 这样你就能把原来的 workflow.py
# 平滑迁移到 LangGraph 风格
# ================================

# TypedDict 用来定义状态结构
# LangGraph 官方推荐围绕共享 State 来流转
from typing import TypedDict, List, Optional

# LangGraph 核心对象
# StateGraph：定义图
# START / END：开始节点和结束节点
from langgraph.graph import StateGraph, START, END

# 导入你项目里现有的模块
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
from llm_router import route_tasks_with_llm


# ================================
# 一、开关配置
# ================================
# 是否使用 LLM 做意图识别
USE_LLM_INTENT = False

# 是否使用 LLM 做订单回答生成
USE_LLM_RESPONSE = True

# 是否使用 LLM Router 做任务路由
USE_LLM_ROUTER = True


# ================================
# 二、定义 LangGraph 的状态结构
# ================================
# 这里不用你之前的 AgentState 类，
# 而是按 LangGraph 常见写法定义一个 TypedDict。
#
# 为什么要这样？
# 因为 LangGraph 图中的每个节点，都会：
# - 读取 state
# - 返回更新后的 state
#
# 所以我们要提前定义清楚 state 里有哪些字段。
class CustomerServiceState(TypedDict, total=False):
    # 用户当前问题
    question: str

    # 基础数据
    products: list
    orders: list
    policy: str

    # 会话记忆对象
    memory: object

    # 安全检查相关
    is_short_followup: bool
    has_context: bool
    is_safe: bool
    guard_message: Optional[str]
    should_stop: bool

    # 中间状态
    intents: List[str]
    tasks: List[str]
    responses: List[str]

    # 最终输出
    final_response: Optional[str]

    # 调试轨迹
    trace: List[str]


# ================================
# 三、辅助函数：记录调试轨迹
# ================================
def add_trace(state: CustomerServiceState, message: str):
    """
    给 state 追加一条轨迹，同时打印出来

    这样在命令行里仍然能看到：
    【安全护栏】通过
    【意图识别】['order_query']
    """
    if "trace" not in state or state["trace"] is None:
        state["trace"] = []

    state["trace"].append(message)
    print(message)


# ================================
# 四、辅助函数：判断是否是追问
# ================================
def is_followup_question(question: str) -> bool:
    """
    判断一句话是不是“短追问”

    例如：
    - 那现在呢
    - 这个呢
    - 那物流呢
    """

    q = question.strip()

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

    if q in explicit_followups:
        return True

    if q.startswith("那") and len(q) <= 8:
        return True

    if (q.startswith("这个") or q.startswith("那个")) and len(q) <= 6:
        return True

    return False


# ================================
# 五、节点函数
# ================================
# LangGraph 的节点函数本质上就是：
# 输入 state
# 做处理
# 返回 state 中需要更新的字段
#
# 注意：
# 这里我为了让你更容易理解，采用“返回字典”的方式。
# LangGraph 会把这些字段合并回总 state。
def guard_node(state: CustomerServiceState):
    """
    安全护栏节点
    """
    question = state["question"]
    products = state["products"]
    memory = state["memory"]

    is_short_followup = is_followup_question(question)

    has_context = (
        memory.get_last_intents() is not None
        or memory.get_last_product() is not None
        or memory.get_last_order() is not None
    )

    # 如果是“短追问 + 有上下文”，直接放行
    if is_short_followup and has_context:
        add_trace(state, "【安全护栏】短追问放行")
        return {
            "is_short_followup": True,
            "has_context": True,
            "is_safe": True,
            "guard_message": None,
            "should_stop": False,
        }

    # 否则正常走安全护栏
    is_safe, guard_message = safety_guard(question, products)

    if is_safe:
        add_trace(state, "【安全护栏】通过")
        return {
            "is_short_followup": is_short_followup,
            "has_context": has_context,
            "is_safe": True,
            "guard_message": None,
            "should_stop": False,
        }
    else:
        add_trace(state, "【安全护栏】拦截")
        return {
            "is_short_followup": is_short_followup,
            "has_context": has_context,
            "is_safe": False,
            "guard_message": guard_message,
            "should_stop": True,
        }


def intent_node(state: CustomerServiceState):
    """
    意图识别节点
    """
    question = state["question"]
    memory = state["memory"]

    # 先正常识别意图
    if USE_LLM_INTENT:
        intents = classify_intents_llm(question)
        if intents is None:
            add_trace(state, "【回退】使用规则版意图识别")
            intents = classify_intents(question)
    else:
        intents = classify_intents(question)

    # 如果当前识别不出来，但又是追问，就尝试继承上一轮意图
    if intents == ["unknown_query"] and state.get("is_short_followup", False):
        last_intents = memory.get_last_intents()
        if last_intents is not None:
            add_trace(state, "【上下文继承】当前问题意图不明显，继承上一轮意图")
            intents = last_intents

    # 写回 memory
    memory.update_intents(intents)

    add_trace(state, f"【意图识别】{intents}")

    return {
        "intents": intents
    }


def planner_node(state: CustomerServiceState):
    """
    任务规划节点
    """
    question = state["question"]
    intents = state["intents"]
    memory = state["memory"]

    # 优先尝试 LLM Router
    if USE_LLM_ROUTER:
        routed_tasks = route_tasks_with_llm(question, memory.response_cache)
        if routed_tasks is not None:
            add_trace(state, f"【LLM Router任务】{routed_tasks}")
            return {"tasks": routed_tasks}
        else:
            add_trace(state, "【LLM Router】失败，回退规则 Planner")

    # 回退规则 Planner
    tasks = build_tasks(intents)
    add_trace(state, f"【Planner任务】{tasks}")
    return {"tasks": tasks}


def execute_node(state: CustomerServiceState):
    """
    执行节点
    """
    question = state["question"]
    products = state["products"]
    orders = state["orders"]
    policy = state["policy"]
    memory = state["memory"]
    tasks = state["tasks"]

    responses = []

    if "price_task" in tasks:
        add_trace(state, "【执行器】执行价格任务")
        responses.append(execute_price_task(question, products, memory))

    if "stock_task" in tasks:
        add_trace(state, "【执行器】执行库存任务")
        responses.append(execute_stock_task(question, products, memory))

    if "order_task" in tasks:
        add_trace(state, "【执行器】执行订单任务")
        responses.append(execute_order_task(question, orders, memory, USE_LLM_RESPONSE))

    if "policy_task" in tasks:
        add_trace(state, "【执行器】执行售后任务")
        responses.append(execute_policy_task(question, policy))

    return {
        "responses": responses
    }


def aggregate_node(state: CustomerServiceState):
    """
    聚合节点
    """
    responses = state.get("responses", [])
    final_response = "\n".join(responses)
    return {"final_response": final_response}


def general_node(state: CustomerServiceState):
    """
    问候分支节点
    """
    add_trace(state, "【分支】进入问候节点")
    return {"final_response": "您好，我是智能客服助手，请问有什么可以帮您？"}


def unknown_node(state: CustomerServiceState):
    """
    兜底分支节点
    """
    add_trace(state, "【分支】进入兜底节点")
    return {"final_response": "抱歉，我暂时没有理解您的问题。您可以问我商品价格、库存、订单或售后政策。"}


def blocked_node(state: CustomerServiceState):
    """
    安全拦截分支节点
    """
    return {"final_response": state.get("guard_message", "抱歉，该问题无法处理。")}


# ================================
# 六、条件分支函数
# ================================
# LangGraph 可以用条件边来决定“下一步去哪个节点”。
def route_after_guard(state: CustomerServiceState):
    """
    安全检查后决定下一步
    """
    if state.get("should_stop", False):
        return "blocked"
    return "intent"


def route_after_intent(state: CustomerServiceState):
    """
    意图识别后决定走哪个分支
    """
    intents = state.get("intents", [])

    if intents == ["general_query"]:
        return "general"

    if intents == ["unknown_query"]:
        return "unknown"

    return "planner"


# ================================
# 七、构建 LangGraph
# ================================
def build_langgraph_app():
    """
    构建并编译 LangGraph 应用
    """

    # 创建图对象，传入 State schema
    graph = StateGraph(CustomerServiceState)

    # 添加节点
    graph.add_node("guard", guard_node)
    graph.add_node("intent", intent_node)
    graph.add_node("planner", planner_node)
    graph.add_node("execute", execute_node)
    graph.add_node("aggregate", aggregate_node)

    graph.add_node("general", general_node)
    graph.add_node("unknown", unknown_node)
    graph.add_node("blocked", blocked_node)

    # 起点：START -> guard
    graph.add_edge(START, "guard")

    # guard 后面走条件分支
    graph.add_conditional_edges(
        "guard",
        route_after_guard,
        {
            "blocked": "blocked",
            "intent": "intent",
        }
    )

    # intent 后面走条件分支
    graph.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "general": "general",
            "unknown": "unknown",
            "planner": "planner",
        }
    )

    # 正常业务链路
    graph.add_edge("planner", "execute")
    graph.add_edge("execute", "aggregate")

    # 所有终点节点都接 END
    graph.add_edge("aggregate", END)
    graph.add_edge("general", END)
    graph.add_edge("unknown", END)
    graph.add_edge("blocked", END)

    # 编译图
    app = graph.compile()

    return app


# ================================
# 八、对外暴露一个运行函数
# ================================
# 这样 main_langgraph.py 或 app_langgraph.py 调用会更方便
langgraph_app = build_langgraph_app()


def run_langgraph_workflow(state_dict: dict):
    """
    运行 LangGraph 工作流

    参数：
    - state_dict：普通字典，里面放 question / products / orders / policy / memory 等

    返回：
    - 执行完成后的 state 字典
    """
    return langgraph_app.invoke(state_dict)