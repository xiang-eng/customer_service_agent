# ================================
# llm_router.py
# 作用：
# 用 LLM 判断当前问题应该调用哪些任务
# 返回任务列表，例如：
# ["price_task", "order_task"]
# 这一版增加了缓存，减少重复路由调用
# ================================

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_client():
    """
    创建大模型客户端
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("未找到 DASHSCOPE_API_KEY，请检查 .env 文件")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=5.0,
    )
    return client


def build_router_prompt(question):
    """
    构造 Router 的提示词
    """
    return f"""
你是一个电商客服系统的任务路由器。
请根据用户问题，判断需要调用哪些任务。

可选任务只有这些：
- price_task：查询价格
- stock_task：查询库存
- order_task：查询订单、物流、发货、签收
- policy_task：查询退货、换货、保修、售后
- general_task：问候
- unknown_task：其他无关问题

要求：
1. 只能返回 JSON
2. 格式必须是：{{"tasks": ["price_task"]}}
3. 如果有多个任务，返回数组
4. 不要输出解释

用户问题：
{question}
""".strip()


def route_tasks_with_llm(question, cache=None):
    """
    用 LLM 决定任务列表

    参数：
    - question：用户问题
    - cache：缓存对象，可选

    返回：
    - 成功：任务列表，例如 ["price_task", "policy_task"]
    - 失败：None
    """

    # =========================
    # 1. 先查缓存
    # =========================
    cache_key = f"router::{question}"

    if cache is not None:
        cached_tasks = cache.get(cache_key)
        if cached_tasks is not None:
            print("【Router缓存命中】直接返回缓存任务")
            return cached_tasks

    # =========================
    # 2. 调用 LLM Router
    # =========================
    client = get_client()

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格返回 JSON 的任务路由器。"
                },
                {
                    "role": "user",
                    "content": build_router_prompt(question)
                }
            ],
            temperature=0
        )

        content = completion.choices[0].message.content.strip()

        result = json.loads(content)
        tasks = result.get("tasks", [])

        if not isinstance(tasks, list) or len(tasks) == 0:
            tasks = ["unknown_task"]

        # =========================
        # 3. 写入缓存
        # =========================
        if cache is not None:
            cache.set(cache_key, tasks)

        return tasks

    except Exception as e:
        print(f"【LLM路由失败】{e}")
        return None