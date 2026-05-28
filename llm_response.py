# =====================================
# llm_response.py
# 作用：
# LLM 回答生成模块
#
# 支持：
# 1. 本地 .env
# 2. Streamlit Cloud Secrets
# 3. DashScope / Qwen
# 4. DeepSeek
#
# 设计原则：
# - 有 DASHSCOPE_API_KEY：优先使用 Qwen
# - 有 DEEPSEEK_API_KEY：使用 DeepSeek
# - 都没有或调用失败：返回 None，让 executors.py 回退模板
# =====================================

import os
import hashlib
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


load_dotenv()


def read_secret(key):
    """
    读取 API Key。

    优先级：
    1. os.environ / .env
    2. Streamlit Cloud 的 st.secrets
    """

    value = os.getenv(key)

    if value:
        return value

    try:
        import streamlit as st

        if key in st.secrets:
            return st.secrets[key]

    except Exception:
        pass

    return None


def clean_api_key(key):
    """
    清洗 API Key，避免复制时带空格或引号。
    """

    if not key:
        return None

    key = str(key).strip()
    key = key.strip('"')
    key = key.strip("'")
    key = key.strip()

    if not key:
        return None

    return key


def get_cache_value(cache, key):
    """
    从缓存中读取回答。
    """

    if cache is None:
        return None

    try:
        return cache.get(key)
    except Exception:
        return None


def set_cache_value(cache, key, value):
    """
    写入回答缓存。
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
    """

    raw = f"{task_type}|{question}|{tool_result}"

    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def get_llm_client():
    """
    创建 LLM 客户端。

    优先使用 DashScope / Qwen。
    如果没有 DashScope Key，再尝试 DeepSeek。
    """

    if OpenAI is None:
        print("【回答生成】openai 包未安装，跳过 LLM 生成")
        return None, None

    dashscope_key = clean_api_key(
        read_secret("DASHSCOPE_API_KEY")
    )

    deepseek_key = clean_api_key(
        read_secret("DEEPSEEK_API_KEY")
    )

    if dashscope_key and dashscope_key != "your_dashscope_api_key_here":
        client = OpenAI(
            api_key=dashscope_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        return client, "qwen-plus"

    if deepseek_key and deepseek_key != "your_deepseek_api_key_here":
        client = OpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com"
        )

        return client, "deepseek-chat"

    print("【回答生成】未配置 DASHSCOPE_API_KEY 或 DEEPSEEK_API_KEY，跳过 LLM 生成")

    return None, None


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
    使用 Qwen / DeepSeek 生成自然语言回答。

    返回：
    - str：LLM 生成回答
    - None：无 Key、API 报错、结果为空时返回 None
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

    client, model = get_llm_client()

    if client is None or model is None:
        return None

    system_prompt = build_system_prompt(task_type)

    user_prompt = build_user_prompt(
        question,
        tool_result
    )

    try:
        response = client.chat.completions.create(
            model=model,
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

        print(f"【回答生成】{model} 生成成功")

        return answer

    except Exception as e:
        print(f"【回答生成失败】{e}")
        return None
