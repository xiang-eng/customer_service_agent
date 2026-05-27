# =====================================
# vision.py
# 使用通义千问VL识别商品图片
# 输出尽量对齐商品库标准名称
# =====================================

import os
import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# =====================================
# 读取 .env
# =====================================

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("DASHSCOPE_API_KEY")

if not api_key:
    raise RuntimeError(
        "没有读取到 DASHSCOPE_API_KEY"
    )


# =====================================
# DashScope OpenAI兼容客户端
# =====================================

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# =====================================
# 商品标准名称（必须和 products.csv 保持一致）
# 按你商品库修改
# =====================================

PRODUCT_CATALOG = [
    "小米智能音箱",
    "苹果无线耳机",
    "华为智能手表"
]


def recognize_product_from_image(uploaded_file):
    """
    识别图片中的商品，
    并尽量返回商品库标准名称
    """

    # 读取图片
    image_bytes = uploaded_file.getvalue()

    # 转 base64
    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    mime_type = uploaded_file.type


    # =========================
    # Prompt
    # =========================
    # 强约束模型只输出商品库名称
    catalog_text = "\n".join(PRODUCT_CATALOG)

    prompt = f"""
你是电商商品识别助手。

请识别图片中的商品。

必须只从下面商品列表中选择一个最匹配的名称输出：

{catalog_text}

规则：
1 只能输出商品名
2 不允许解释
3 不允许输出额外文字
4 必须原样输出列表中的名字
"""


    # =========================
    # 调视觉模型
    # =========================
    response = client.chat.completions.create(
        model="qwen-vl-max",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type":"text",
                        "text":prompt
                    },
                    {
                        "type":"image_url",
                        "image_url":{
                            "url": (
                                f"data:{mime_type};base64,"
                                f"{image_base64}"
                            )
                        }
                    }
                ]
            }
        ]
    )


    result = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


    # =========================
    # 双保险：
    # 如果模型输出不在商品库
    # 做关键词兜底
    # =========================

    if result in PRODUCT_CATALOG:
        return result

    if "小米" in result:
        return "小米智能音箱"

    if "苹果" in result:
        return "苹果无线耳机"

    if "华为" in result:
        return "华为智能手表"

    return result