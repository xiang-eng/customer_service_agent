# =====================================
# multi_agent.py
# 作用：
# Multi-Agent + Agentic RAG 版本客服系统
#
# 核心流程：
# 1. SafetyAgent      安全检查
# 2. IntentAgent      意图识别
# 3. PlannerAgent     任务规划
# 4. RetrievalRouter  动态工具检索
# 5. ReflectionAgent  检查答案是否足够
# 6. 如果不足，重新规划并再次检索
# =====================================

from safety import safety_guard
from intent import classify_intents
from llm_router import route_tasks_with_llm

from executors import (
    execute_price_task,
    execute_stock_task,
    execute_order_task,
    execute_policy_task,
)

from planner_agentic import build_agentic_tasks

from retrieval_router import route_and_retrieve

from reflection_agent import (
    evidence_enough,
    reflect_and_replan,
)


# 是否启用 LLM Router
# 是否启用 LLM Router
USE_LLM_ROUTER = False

# 是否启用 LLM 订单回答生成
USE_LLM_RESPONSE = True


def is_followup_question(question):
    """
    判断用户是不是短追问。

    例如：
    - 那现在呢
    - 这个呢
    - 那物流呢
    """

    q = question.strip()

    followups = [
        "那现在呢",
        "现在呢",
        "这个呢",
        "那个呢",
        "那物流呢",
        "那订单呢",
        "那价格呢",
        "那库存呢",
        "那退货呢",
        "那换货呢",
    ]

    if q in followups:
        return True

    if q.startswith("那") and len(q) <= 8:
        return True

    if (q.startswith("这个") or q.startswith("那个")) and len(q) <= 6:
        return True

    return False


class SafetyAgent:
    """
    安全 Agent。

    负责判断：
    - 用户问题能不能处理
    - 是否涉及隐私
    - 是否超出业务范围
    """

    def run(self, question, products, memory):
        """
        返回：
        - is_safe：是否通过
        - message：拦截原因或“通过”
        """

        is_followup = is_followup_question(question)

        has_context = (
            memory.get_last_product() is not None
            or memory.get_last_order() is not None
            or memory.get_last_intents() is not None
        )

        if is_followup and has_context:
            return True, "短追问放行"

        return safety_guard(question, products)


class IntentAgent:
    """
    意图识别 Agent。

    负责判断用户在问什么：
    - 价格
    - 库存
    - 订单
    - 售后
    - 问候
    - 未知问题
    """

    def run(self, question, memory, is_followup=False):
        """
        返回意图列表。
        """

        intents = classify_intents(question)

        if intents == ["unknown_query"] and is_followup:
            last_intents = memory.get_last_intents()

            if last_intents is not None:
                print("【IntentAgent】继承上一轮意图")
                intents = last_intents

        memory.update_intents(intents)

        return intents


class PlannerAgent:
    """
    任务规划 Agent。

    普通版本：
    price_query → price_task

    Agentic RAG 版本：
    会进一步判断多跳任务。
    """

    def run(self, question, intents, memory):
        """
        返回任务列表。
        """

        if USE_LLM_ROUTER:
            tasks = route_tasks_with_llm(
                question,
                memory.response_cache
            )

            if tasks is not None:
                print(f"【PlannerAgent】LLM Router任务：{tasks}")

                agentic_tasks = build_agentic_tasks(
                    question,
                    intents
                )

                for task in agentic_tasks:
                    if task not in tasks:
                        tasks.append(task)

                print(f"【PlannerAgent】Agentic增强后任务：{tasks}")

                return tasks

            print("【PlannerAgent】LLM Router失败，回退规则Planner")

        tasks = build_agentic_tasks(
            question,
            intents
        )

        print(f"【PlannerAgent】Agentic规则任务：{tasks}")

        return tasks


class ToolAgent:
    """
    工具调用 Agent。

    注意：
    在 Agentic RAG 版本中，
    主要由 retrieval_router.py 调用工具。

    这个类保留是为了兼容旧代码。
    """

    def run(self, question, tasks, products, orders, policy, memory):
        """
        根据任务列表逐个调用工具。
        """

        responses = []

        if "price_task" in tasks:
            print("【ToolAgent】调用价格工具")
            result = execute_price_task(question, products, memory)
            responses.append(result)

        if "stock_task" in tasks:
            print("【ToolAgent】调用库存工具")
            result = execute_stock_task(question, products, memory)
            responses.append(result)

        if "order_task" in tasks:
            print("【ToolAgent】调用订单工具")
            result = execute_order_task(
                question,
                orders,
                memory,
                USE_LLM_RESPONSE
            )
            responses.append(result)

        if "policy_task" in tasks:
            print("【ToolAgent】调用售后RAG工具")
            result = execute_policy_task(question, policy)
            responses.append(result)

        return responses


class ValidatorAgent:
    """
    结果校验 Agent。

    负责检查工具返回结果是否为空，
    并做简单清洗。

    在 Agentic RAG 版本中，
    更强的校验由 ReflectionAgent 完成。
    """

    def run(self, responses):
        """
        返回清洗后的 responses。
        """

        cleaned = []

        for response in responses:
            if response is None:
                continue

            response = response.strip()

            if not response:
                continue

            if response not in cleaned:
                cleaned.append(response)

        return cleaned


class CoordinatorAgent:
    """
    总协调 Agent。

    Agentic RAG 版本主流程：

    SafetyAgent
    → IntentAgent
    → PlannerAgent
    → RetrievalRouter
    → ReflectionAgent
        如果答案不好：
        → Replan
        → Retrieve again
    → Final Answer
    """

    def __init__(self, products, orders, policy, memory):
        """
        初始化，把基础数据和 memory 保存下来。
        """

        self.products = products
        self.orders = orders
        self.policy = policy
        self.memory = memory

        self.safety_agent = SafetyAgent()
        self.intent_agent = IntentAgent()
        self.planner_agent = PlannerAgent()

        # 保留旧 ToolAgent 和 ValidatorAgent
        self.tool_agent = ToolAgent()
        self.validator_agent = ValidatorAgent()

    def run(self, question):
        """
        Agentic RAG 主流程。
        """

        print("========== Agentic RAG 协作开始 ==========")

        # 1. 安全检查
        is_safe, message = self.safety_agent.run(
            question,
            self.products,
            self.memory
        )

        print(f"【SafetyAgent】{message}")

        if not is_safe:
            return message

        # 2. 判断是否短追问
        is_followup = is_followup_question(question)

        # 3. 意图识别
        intents = self.intent_agent.run(
            question,
            self.memory,
            is_followup=is_followup
        )

        print(f"【IntentAgent】意图：{intents}")

        # 4. 问候分支
        if intents == ["general_query"]:
            return "您好，我是智能客服助手，请问有什么可以帮您？"

        # 5. 未知问题分支
        if intents == ["unknown_query"]:
            return "抱歉，我暂时没有理解您的问题。您可以问我商品价格、库存、订单或售后政策。"

        # 6. Agentic 任务规划
        tasks = self.planner_agent.run(
            question,
            intents,
            self.memory
        )

        # 7. Agentic RAG 循环
        max_retry = 3

        final_answer = ""
        evidence = []

        for attempt in range(1, max_retry + 1):
            print(f"【AgenticLoop】第 {attempt} 轮检索，任务：{tasks}")

            final_answer, evidence = route_and_retrieve(
                question=question,
                tasks=tasks,
                products=self.products,
                orders=self.orders,
                policy=self.policy,
                memory=self.memory,
                use_llm_response=USE_LLM_RESPONSE
            )

            print(f"【AgenticLoop】本轮回答：{final_answer}")

            ok = evidence_enough(
                final_answer,
                evidence
            )

            if ok:
                print("【ReflectionAgent】证据充分，结束循环")
                break

            print("【ReflectionAgent】证据不足，需要重新规划")

            tasks = reflect_and_replan(
                question,
                tasks,
                attempt
            )

        # 8. 最终兜底
        if not final_answer:
            return "抱歉，我暂时没有找到相关信息。"

        print("========== Agentic RAG 协作结束 ==========")

        return final_answer