# =====================================
# app_streamlit.py
# 作用：
# Streamlit 网页版电商智能客服 Demo
#
# 运行命令：
# streamlit run app_streamlit.py
# =====================================

import streamlit as st

from multi_agent import CoordinatorAgent


class SimpleCache:
    """
    简单缓存类。

    作用：
    兼容项目里可能用到的 response_cache.get()
    和 response_cache.set()
    """

    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data


class Memory:
    """
    会话记忆类。

    作用：
    保存最近一次商品、订单、意图，
    支持多轮追问。
    """

    def __init__(self):
        self.last_product = None
        self.last_order = None
        self.last_intents = None
        self.response_cache = SimpleCache()

    def get_last_product(self):
        return self.last_product

    def update_product(self, product):
        self.last_product = product

    def get_last_order(self):
        return self.last_order

    def update_order(self, order):
        self.last_order = order

        product_name = order.get("product_name") or order.get("product")

        if product_name:
            self.last_product = {
                "name": product_name,
                "product_name": product_name
            }

    def get_last_intents(self):
        return self.last_intents

    def update_intents(self, intents):
        self.last_intents = intents


products = [
    {
        "id": "P1001",
        "name": "华为 Mate 60",
        "product_name": "华为 Mate 60",
        "category": "手机",
        "brand": "华为",
        "aliases": ["华为 Mate 60", "Mate 60", "华为手机", "华为"],
        "price": 6999,
        "stock": 8
    },
    {
        "id": "P1002",
        "name": "小米 14",
        "product_name": "小米 14",
        "category": "手机",
        "brand": "小米",
        "aliases": ["小米 14", "小米14", "小米手机", "小米"],
        "price": 3999,
        "stock": 0
    },
    {
        "id": "P1003",
        "name": "小米智能音箱",
        "product_name": "小米智能音箱",
        "category": "智能音箱",
        "brand": "小米",
        "aliases": ["小米智能音箱", "智能音箱", "音箱"],
        "price": 199,
        "stock": 20
    }
]


orders = [
    {
        "order_id": "O1001",
        "product": "小米智能音箱",
        "product_name": "小米智能音箱",
        "status": "已发货",
        "order_status": "已发货",
        "amount": 199,
        "pay_amount": 199,
        "logistics_company": "顺丰",
        "tracking": "SF123456",
        "tracking_no": "SF123456",
        "tracking_number": "SF123456",
        "logistics_status": "运输中",
        "shipping_status": "运输中"
    },
    {
        "order_id": "O1002",
        "product": "华为 Mate 60",
        "product_name": "华为 Mate 60",
        "status": "待发货",
        "order_status": "待发货",
        "amount": 6999,
        "pay_amount": 6999,
        "logistics_company": "暂无",
        "tracking": "暂无运单",
        "tracking_no": "暂无运单",
        "tracking_number": "暂无运单",
        "logistics_status": "待发货",
        "shipping_status": "待发货"
    }
]


policy = """
售后政策：
1. 未拆封商品支持 7 天无理由退货。
2. 已拆封但无质量问题的商品，不支持无理由退货。
3. 如果商品存在质量问题，支持 15 天内换货。
4. 保修期内非人为损坏，可申请维修。
5. 退款将在退货商品入库并检测通过后 3-7 个工作日原路退回。
"""


def init_agent():
    """
    初始化 Agent。
    使用 st.session_state 保证网页刷新前多轮对话记忆不丢失。
    """

    if "memory" not in st.session_state:
        st.session_state.memory = Memory()

    if "agent" not in st.session_state:
        st.session_state.agent = CoordinatorAgent(
            products=products,
            orders=orders,
            policy=policy,
            memory=st.session_state.memory
        )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "您好，我是电商智能客服助手，请问有什么可以帮您？"
            }
        ]


def reset_chat():
    """
    重置会话。
    """

    st.session_state.memory = Memory()

    st.session_state.agent = CoordinatorAgent(
        products=products,
        orders=orders,
        policy=policy,
        memory=st.session_state.memory
    )

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "您好，我是电商智能客服助手，请问有什么可以帮您？"
        }
    ]


def main():
    st.set_page_config(
        page_title="Agentic RAG 电商智能客服",
        page_icon="🤖",
        layout="wide"
    )

    init_agent()

    st.title("🤖 Multi-Agent + Agentic RAG 电商智能客服")
    st.caption("支持商品价格、库存、订单物流、售后政策、多轮追问和多跳任务规划")

    st.markdown("### 🚀 系统能力")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("商品价格 / 库存查询")

    with col2:
        st.info("订单物流查询")

    with col3:
        st.info("售后政策 RAG")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.success("多跳任务规划")

    with col5:
        st.success("Reflection 自动反思")

    with col6:
        st.success("Memory 上下文追问")

    st.divider()

    st.markdown("### 🧾 当前会话记忆")

    memory = st.session_state.memory

    last_product = memory.get_last_product()
    last_order = memory.get_last_order()
    last_intents = memory.get_last_intents()

    m1, m2, m3 = st.columns(3)

    with m1:
        if last_product:
            product_name = last_product.get("product_name") or last_product.get("name") or "未知商品"
            st.metric("最近商品", product_name)
        else:
            st.metric("最近商品", "暂无")

    with m2:
        if last_order:
            st.metric("最近订单", last_order.get("order_id", "未知订单"))
        else:
            st.metric("最近订单", "暂无")

    with m3:
        if last_intents:
            st.metric("最近意图", ", ".join(last_intents))
        else:
            st.metric("最近意图", "暂无")

    st.divider()


    with st.sidebar:
        st.header("📌 项目信息")

        st.markdown(
            """
            **核心架构：**

            - SafetyAgent
            - IntentAgent
            - PlannerAgent
            - RetrievalRouter
            - ReflectionAgent

            **Agentic RAG 闭环：**

            Plan → Retrieve → Reflect → Re-plan
            """
        )

        st.divider()

        st.header("🧪 示例问题")

        examples = [
            "华为 Mate 60 多少钱？",
            "华为 Mate 60 有货吗？",
            "小米 14 有货吗？",
            "我的订单 O1001 到哪了？",
            "我的订单 O1001 里的商品可以退货吗？",
            "那退货呢？",
            "那物流呢？"
        ]

        for example in examples:
            if st.button(example):
                st.session_state.pending_question = example

        st.divider()

        if st.button("🔄 清空对话"):
            reset_chat()
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("请输入你的问题，例如：我的订单 O1001 可以退货吗？")

    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question

    if user_input:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Agent 正在规划任务、调用工具并反思答案..."):
                answer = st.session_state.agent.run(user_input)

            st.write(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


if __name__ == "__main__":
    main()