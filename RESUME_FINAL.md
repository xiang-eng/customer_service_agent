# 简历最终版项目描述

## 项目名称

Multi-Agent + Agentic RAG 电商智能客服系统

---

## 简历写法一：推荐正式版

Multi-Agent + Agentic RAG 电商智能客服系统

- 设计并实现基于 Python 的 Multi-Agent + Agentic RAG 电商智能客服系统，支持商品价格、库存、订单物流、售后政策问答和多轮上下文追问。
- 构建 SafetyAgent、IntentAgent、PlannerAgent、RetrievalRouter、ReflectionAgent 多 Agent 协作流程，实现安全检查、意图识别、任务规划、工具调用、证据反思和自动重规划。
- 实现商品库、订单库、售后政策 RAG 多工具动态路由，支持价格查询、库存查询、订单查询、物流查询和售后政策问答。
- 针对“我的订单 O1001 里的商品可以退货吗？”等多跳问题，自动拆分为 order_task + policy_task，并融合订单信息与售后政策生成回答。
- 引入 Memory 机制，维护 last_product、last_order、last_intents，实现“那退货呢”“那物流呢”等省略主语场景下的上下文继承。
- 基于 Streamlit 搭建网页端交互 Demo，支持多轮对话演示，并完善 README、运行说明、架构文档和面试总结文档。

---

## 简历写法二：简短版

Multi-Agent + Agentic RAG 电商智能客服系统：基于 Python 实现多 Agent 协作客服系统，包含意图识别、任务规划、工具路由、RAG 检索、Reflection 反思重规划和 Memory 上下文追问能力；支持商品、订单、售后政策多场景问答，并基于 Streamlit 实现网页端 Demo。

---

## 简历写法三：AI 应用方向

基于 Python 实现 Multi-Agent + Agentic RAG 电商智能客服系统，构建 Safety、Intent、Planner、Retrieval、Reflection 多 Agent 协作流程，实现任务规划、工具调用、证据反思、自动重规划和上下文记忆能力。系统支持商品、订单、售后政策等多源数据检索，并通过 Streamlit 提供网页端 Demo 展示。

---

## 简历写法四：后端 / 工程方向

实现电商智能客服系统后端逻辑，完成商品查询、订单查询、售后政策问答等核心业务模块。系统采用 Multi-Agent 架构进行模块解耦，通过 PlannerAgent 进行任务规划，通过 RetrievalRouter 动态调用商品、订单、RAG 工具，并引入 ReflectionAgent 对回答进行证据校验和自动重试，提升系统鲁棒性和可解释性。

---

## 技术栈关键词

Python
Streamlit
Multi-Agent
Agentic RAG
RAG
Tool Calling
Memory
Reflection
Task Planning
Chroma
BM25
LLM Application
Prompt Engineering

---

## 面试时可以强调的关键词

1. 不是普通 FAQ，而是 Agentic RAG。
2. 不是单轮问答，而是支持多轮上下文追问。
3. 不是单工具查询，而是多工具动态路由。
4. 不是一次检索结束，而是有 Reflection 和 Re-plan。
5. 不只是代码实现，还做了 Streamlit 网页 Demo 和 GitHub 项目包装。
