# =====================================
# llm_react_agent.py
# 作用：
# LLM 驱动的 ReAct Agent
#
# 当前版本支持“多 Action”
#
# 核心流程：
# 1. Thought：让 LLM 分析用户问题
# 2. Actions：让 LLM 选择一个或多个工具
# 3. Observation：Python 逐个调用真实工具
# 4. Final Answer：合并多个观察结果，生成最终回答
# =====================================

import json
import os

from openai import OpenAI
from dotenv import load_dotenv

from tools import find_product, find_order, search_policy


# 读取 .env 文件里的 DASHSCOPE_API_KEY
load_dotenv()


def get_client():
    """
    创建大模型客户端
    """

    # 从环境变量读取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")

    # 如果没有读取到，就报错提醒
    if not api_key:
        raise ValueError("未找到 DASHSCOPE_API_KEY，请检查 .env 文件")

    # 创建 OpenAI 兼容客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=5.0,
    )

    return client


class LLMReActAgent:
    """
    LLM 驱动的 ReAct Agent

    特点：
    - LLM 负责 Thought 和 Actions 选择
    - Python 负责真正调用工具
    - 支持一个问题触发多个 Action
    """

    def __init__(self, products, orders, policy):
        """
        初始化 Agent

        参数：
        - products：商品列表
        - orders：订单列表
        - policy：售后政策文本
        """

        # 保存商品数据
        self.products = products

        # 保存订单数据
        self.orders = orders

        # 保存售后政策
        self.policy = policy

        # 创建大模型客户端
        self.client = get_client()

    def build_action_prompt(self, question):
        """
        构造提示词，让 LLM 选择一个或多个 Action

        注意：
        这里要求 LLM 返回 actions 数组，
        而不是单个 action。
        """

        return f"""
你是一个电商客服 ReAct Agent 的动作选择器。

你只能从下面这些 Action 中选择：

1. product_price
   用于查询商品价格

2. product_stock
   用于查询商品库存

3. order_query
   用于查询订单、物流、发货、签收

4. policy_query
   用于查询退货、换货、保修、售后政策

5. unknown
   用于无法理解或不属于客服范围的问题

请根据用户问题选择需要执行的 Action。
如果用户问题里包含多个需求，请返回多个 Action。

严格要求：
- 只能输出 JSON
- 不要输出解释
- JSON 格式必须是：
{{"thought": "你的简短思考", "actions": ["product_price"]}}
- 如果是多个任务，例如同时问价格和售后，则返回：
{{"thought": "用户同时询问价格和售后", "actions": ["product_price", "policy_query"]}}
- 如果无法处理，则返回：
{{"thought": "问题不属于客服范围", "actions": ["unknown"]}}

用户问题：
{question}
""".strip()

    def think_and_choose_actions(self, question):
        """
        Thought + Actions

        让 LLM 分析用户问题，并选择一个或多个 actions。

        返回：
        - actions 列表，例如：
          ["product_price", "order_query"]
        """

        print("Thought: 让 LLM 分析用户问题并选择工具...")

        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个严格输出 JSON 的 ReAct Agent 动作选择器。"
                    },
                    {
                        "role": "user",
                        "content": self.build_action_prompt(question)
                    }
                ],
                temperature=0
            )

            # 取出模型返回内容
            content = completion.choices[0].message.content.strip()

            # 把 JSON 字符串解析成 Python 字典
            result = json.loads(content)

            # 取 thought
            thought = result.get("thought", "")

            # 取 actions
            actions = result.get("actions", ["unknown"])

            # 如果模型返回的 actions 不是列表，就兜底成 unknown
            if not isinstance(actions, list):
                actions = ["unknown"]

            # 如果 actions 是空列表，也兜底
            if len(actions) == 0:
                actions = ["unknown"]

            print(f"Thought: {thought}")
            print(f"Actions: {actions}")

            return actions

        except Exception as e:
            print(f"【LLM ReAct 动作选择失败】{e}")
            return ["unknown"]

    def act(self, action, question):
        """
        根据某一个 action 调用真实工具

        参数：
        - action：一个动作，例如 product_price
        - question：用户问题

        返回：
        - 工具返回结果
        """

        print(f"Action: 调用工具 -> {action}")

        if action == "product_price":
            return find_product(question, self.products)

        if action == "product_stock":
            return find_product(question, self.products)

        if action == "order_query":
            return find_order(question, self.orders)

        if action == "policy_query":
            return search_policy(question, self.policy)

        return None

    def observe(self, action, tool_result):
        """
        Observation：把某个工具返回结果整理成观察信息

        参数：
        - action：当前执行的动作
        - tool_result：工具返回结果

        返回：
        - 一段观察文本
        """

        print("Observation: 工具返回结果")

        if tool_result is None:
            return "工具未找到相关结果。"

        if action == "product_price":
            price = int(tool_result["price"]) if tool_result["price"].is_integer() else tool_result["price"]
            return f"{tool_result['name']} 的价格是 {price} 元。"

        if action == "product_stock":
            return f"{tool_result['name']} 当前库存为 {tool_result['stock']} 件。"

        if action == "order_query":
            pay_amount = int(tool_result["pay_amount"]) if tool_result["pay_amount"].is_integer() else tool_result["pay_amount"]

            return (
                f"订单 {tool_result['order_id']} 当前状态为：{tool_result['order_status']}。\n"
                f"商品：{tool_result['product_name']}，支付金额：{pay_amount} 元。\n"
                f"物流公司：{tool_result['logistics_company']}，物流单号：{tool_result['tracking_number']}。\n"
                f"物流状态：{tool_result['shipping_status']}。"
            )

        if action == "policy_query":
            return f"根据我们的售后政策：\n{tool_result}"

        return "暂时没有可用的观察结果。"

    def final_answer(self, observations):
        """
        Final Answer：合并多个 Observation

        参数：
        - observations：多个观察结果组成的列表

        返回：
        - 最终客服回答
        """

        print("Final Answer: 合并观察结果生成最终回复")

        # 如果没有观察结果，就兜底
        if not observations:
            return "客服：抱歉，我暂时没有找到相关信息。"

        # 用换行拼接多个观察结果
        final_text = "\n".join(observations)

        return "客服：" + final_text

    def run(self, question):
        """
        运行完整 LLM ReAct 多工具流程
        """

        # 1. Thought + Actions
        actions = self.think_and_choose_actions(question)

        # 如果只返回 unknown，就直接兜底
        if actions == ["unknown"]:
            return "客服：抱歉，我暂时没有理解您的问题。"

        observations = []

        # 2. 逐个执行 Action
        for action in actions:
            # 如果 action 是 unknown，跳过
            if action == "unknown":
                continue

            # Action：调用工具
            tool_result = self.act(action, question)

            # Observation：整理工具结果
            observation = self.observe(action, tool_result)

            # 保存观察结果
            observations.append(observation)

        # 3. Final Answer：合并多个观察结果
        return self.final_answer(observations)