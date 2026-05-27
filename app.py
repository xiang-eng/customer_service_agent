# =====================================
# app.py
# Streamlit 多模态智能客服（稳定版）
#
# 支持：
# 1 文本提问
# 2 图片上传
# 3 自动商品识别
# 4 图片+文本联合输入
# 5 Multi-Agent客服
# =====================================

import streamlit as st

from dataloader import (
    load_products,
    load_orders,
    load_policy
)

from memory import SessionMemory

from multi_agent import CoordinatorAgent

from vision import recognize_product_from_image


# =====================================
# 页面标题
# =====================================

st.title(
    "🤖 智能客服 Multi-Agent + Multimodal Demo"
)

st.write(
"""
支持：

- 商品价格查询
- 库存查询
- 订单物流查询
- 售后政策问答
- 图片自动识别 + 文本联合输入
"""
)


# =====================================
# 初始化 Agent
# =====================================

@st.cache_resource
def init_agent():

    products = load_products()

    orders = load_orders()

    policy = load_policy()

    memory = SessionMemory()

    agent = CoordinatorAgent(
        products=products,
        orders=orders,
        policy=policy,
        memory=memory
    )

    return agent


agent = init_agent()


# =====================================
# Session State 初始化
# =====================================

if "image_hint" not in st.session_state:
    st.session_state.image_hint = ""

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = ""



# =====================================
# 图片上传（自动识别）
# =====================================

uploaded_file = st.file_uploader(
    "上传商品图片",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file:

    st.image(
        uploaded_file,
        caption="用户上传图片",
        use_container_width=True
    )


    # 只有上传新图片才重新识别
    if (
        uploaded_file.name
        != st.session_state.last_uploaded_name
    ):

        with st.spinner("自动识别图片中..."):

            result = recognize_product_from_image(
                uploaded_file
            )

            st.session_state.image_hint = result

            st.session_state.last_uploaded_name = (
                uploaded_file.name
            )


    if st.session_state.image_hint:

        st.success(
            f"识别结果：{st.session_state.image_hint}"
        )



# =====================================
# 用户输入
# =====================================

question = st.text_input(
    "请输入问题",
    placeholder="例如：这个多少钱？"
)



# =====================================
# 发送按钮
# =====================================

if st.button("发送"):

    if not question:

        st.warning("请输入问题")

        st.stop()


    # ==========================
    # 多模态融合
    # ==========================

    if st.session_state.image_hint:

        final_question = (
            st.session_state.image_hint
            + " "
            + question
        )

    else:

        final_question = question


    # 调试输出
    st.warning(
        f"最终送进Agent的问题：{final_question}"
    )


    # ==========================
    # 调 Agent
    # ==========================

    with st.spinner(
        "Agent处理中..."
    ):

        response = agent.run(
            final_question
        )


    st.success(
        "客服回复"
    )

    st.write(
        response
    )



# =====================================
# 清空上下文（可选）
# =====================================

if st.button("清空图片上下文"):

    st.session_state.image_hint = ""

    st.session_state.last_uploaded_name = ""

    st.success("图片上下文已清空")