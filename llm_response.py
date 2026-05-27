import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_client():
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("未找到 DASHSCOPE_API_KEY，请检查 .env 文件")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=5.0,
    )
    return client


def build_response_prompt(question, tool_result, task_type):
    """
    构造回答生成提示词
    question: 用户问题
    tool_result: 工具查询结果（字符串）
    task_type: 当前任务类型，例如 order_task
    """

    task_instruction_map = {
        "order_task": "你只能回答订单、物流、发货、签收相关信息，不要回答价格、库存、售后政策。",
        "price_task": "你只能回答价格相关信息，不要回答订单、库存、售后政策。",
        "stock_task": "你只能回答库存相关信息，不要回答价格、订单、售后政策。",
        "policy_task": "你只能回答售后、退货、换货、保修相关信息，不要回答价格、库存、订单。"
    }

    task_instruction = task_instruction_map.get(
        task_type,
        "你只能回答当前任务对应的信息，不要扩展。"
    )

    return f"""
你是一个电商客服助手。
请根据用户问题和系统查到的结果，生成自然、简洁、准确的中文回答。

严格要求：
1. 只能基于“系统查到的结果”回答
2. 不要编造任何未提供的信息
3. {task_instruction}
4. 严禁回答非本任务内容，也不要解释其他任务
5. 如果当前任务无关，不要解释，直接忽略
6. 不要输出 JSON

用户问题：
{question}

当前任务类型：
{task_type}

系统查到的结果：
{tool_result}

请直接输出最终回复：
""".strip()


def generate_response_with_llm(question, tool_result, cache=None, task_type="order_task"):
    """
    用 LLM 把工具结果整理成更自然的客服回答

    参数：
    - question: 用户问题
    - tool_result: 工具查询结果
    - cache: 缓存对象（SimpleCache）
    - task_type: 当前任务类型
    """

    # 用 question + tool_result + task_type 组成缓存 key
    cache_key = f"{task_type}||{question}||{tool_result}"

    # 如果传入了缓存对象，就先查缓存
    if cache is not None:
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            print("【缓存命中】直接返回缓存回答")
            return cached_response

    client = get_client()

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个严格受约束的电商客服助手，只能基于给定结果回答。"},
                {"role": "user", "content": build_response_prompt(question, tool_result, task_type)},
            ],
            temperature=0.2,
        )

        content = completion.choices[0].message.content.strip()

        # 如果有缓存对象，就把新结果写入缓存
        if cache is not None:
            cache.set(cache_key, content)

        return content

    except Exception as e:
        print(f"【回答生成失败】{e}")
        return None