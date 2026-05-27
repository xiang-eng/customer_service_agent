import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def get_client():
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("未找到 DASHSCOPE_API_KEY，请检查 .env 文件")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=5.0,  # 给请求设置超时时间
    )
    return client


def build_prompt(question: str) -> str:
    return f"""
你是一个电商客服系统的意图识别器。
请根据用户问题，从以下标签中选择一个或多个：

- price_query：查询价格
- stock_query：查询库存
- policy_query：查询退货、换货、售后、保修、质量问题
- order_query：查询订单、物流、发货、签收
- general_query：问候语
- unknown_query：其他无关问题

要求：
1. 只返回 JSON
2. JSON 格式必须是：{{"intents": ["price_query"]}}
3. 如果是多个意图，按数组返回
4. 如果无法归类，返回 unknown_query

示例：
用户：小米智能音箱多少钱？
输出：{{"intents": ["price_query"]}}

用户：华为门铃还有货吗？可以退货吗？
输出：{{"intents": ["stock_query", "policy_query"]}}

用户：订单 O1001 到哪了？
输出：{{"intents": ["order_query"]}}

用户：你好
输出：{{"intents": ["general_query"]}}

用户：今天天气怎么样？
输出：{{"intents": ["unknown_query"]}}

现在请判断：
用户：{question}
""".strip()


def classify_intents_llm(question: str):
    print("【调试】当前 LLM 超时设置：5 秒，失败后直接回退")
    client = get_client()

    last_error = None

    # 最多重试 2 次
    for attempt in range(1):
        try:
            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个严格返回 JSON 的意图识别器。"},
                    {"role": "user", "content": build_prompt(question)},
                ],
                temperature=0,
            )

            content = completion.choices[0].message.content.strip()

            try:
                result = json.loads(content)
                intents = result.get("intents", [])#从字典里取 intents，如果没有就给空列表
                if not intents:
                    return ["unknown_query"]
                return intents
            except Exception:
                return ["unknown_query"]

        except Exception as e:
            last_error = e
            print(f"【LLM调用失败，第 {attempt + 1} 次】{e}")
            time.sleep(1)#暂停 1 秒

    # 两次都失败，返回 None，让上层回退规则版
    print("【LLM调用最终失败，准备回退到规则版】")
    return None
