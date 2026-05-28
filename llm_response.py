# =====================================
# llm_response.py
# 作用：
# LLM 回答生成模块
#
# 当前版本支持 DeepSeek API。
#
# 设计原则：
# 1. 有 API Key：调用 DeepSeek 生成自然语言回答
# 2. 没有 API Key：返回 None，让 executors.py 自动回退模板
# 3. API 报错：返回 None，不影响主流程
# =====================================

import os
import hashlib
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# 读取 .env 文件
load_dotenv()


def get_cache_value(cache, key):
    """
    从缓存中读取数据。

    兼容两种写法：
    1. 普通 dict：cache.get(key)
    2. 自定义缓存对象：cache.get(key)
    """

    if cache is None:
        return None

    try:
        return cache.get(key)
    except Exception:
        return None


def set_cache_value(cache, key, value):
    """
    向缓存中写入数据。

    兼容两种写法：
    1. 普通 dict：cache[key] = value
    2. 自定义缓存对象：cache.set(key, value)
    """

    if cache is None:
        return

    try:
        if hasattr(cache, "set"):
            cache.set(key, value)
        elif isinstance(cache, dict):
            cache[key] = value
    except Exception:
        return


def build_cache_key(question, tool_result, task_type):
    """
    构造缓存 key。

    同一个问题 + 同一个工具结果 + 同一个任务类型，
    生成相同 key，避免重复调用 API。
    """

    raw = f"{task_type}|{question}|{tool_result}"

    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def get_deepseek_client():
    """
    创建 DeepSeek 客户端。

    DeepSeek API 兼容 OpenAI SDK，
    只需要改 base_url。
    """

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("【回答生成】未配置 DEEPSEEK_API_KEY，跳过 LLM 生成")
        return None

    if OpenAI is None:
        print("【回答生成】openai 包未安装，跳过 LLM 生成")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    return client


def build_system_prompt(task_type):
    """
    根据任务类型构造 system prompt。
    """

    if task_type == "order_task":
        return (
            "你是一个电商客服助手。"
            "你需要严格根据工具返回的订单事实回答用户。"
            "不要编造订单状态、物流公司、物流单号、金额。"
            "如果工具结果中没有的信息，不要自己补充。"
            "回答要自然、简洁、礼貌。"
        )

    if task_type == "policy_task":
        return (
            "你是一个电商售后客服助手。"
            "你需要严格根据给定的售后政策内容回答用户。"
            "不要编造政策。"
            "回答要清晰、简洁、适合客服场景。"
        )

    return (
        "你是一个电商智能客服助手。"
        "请严格根据工具结果回答用户问题。"
        "不要编造事实。"
    )


def build_user_prompt(question, tool_result):
    """
    构造用户 prompt。
    """

    return f"""
用户问题：
{question}

工具返回的事实信息：
{tool_result}

请根据以上事实信息，生成一段自然、准确、简洁的客服回答。
"""


def generate_response_with_llm(
    question,
    tool_result,
    response_cache=None,
    task_type="general_task"
):
    """
    使用 DeepSeek API 生成自然语言回答。

    参数：
    - question：用户原始问题
    - tool_result：工具返回的事实信息
    - response_cache：回答缓存，可传 dict 或自定义缓存对象
    - task_type：任务类型，例如 order_task / policy_task

    返回：
    - str：LLM 生成的回答
    - None：没有 API Key、API 报错、结果为空时返回 None
    """

    cache_key = build_cache_key(
        question,
        tool_result,
        task_type
    )

    cached_answer = get_cache_value(
        response_cache,
        cache_key
    )

    if cached_answer:
        print("【回答生成】命中 LLM 缓存")
        return cached_answer

    client = get_deepseek_client()

    if client is None:
        return None

    system_prompt = build_system_prompt(task_type)

    user_prompt = build_user_prompt(
        question,
        tool_result
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.3,
            max_tokens=500,
            timeout=20
        )

        answer = response.choices[0].message.content

        if answer is None:
            return None

        answer = answer.strip()

        if not answer:
            return None

        set_cache_value(
            response_cache,
            cache_key,
            answer
        )

        print("【回答生成】DeepSeek 生成成功")

        return answer

    except Exception as e:
        print(f"【回答生成失败】{e}")
        return None
