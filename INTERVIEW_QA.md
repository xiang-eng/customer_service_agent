# 项目面试高频问答

## Q1：项目是做什么的？

这是一个基于 Multi-Agent + Agentic RAG 的电商智能客服系统。

支持：

- 商品查询
- 订单查询
- 售后政策问答
- 多轮上下文追问

---

## Q2：为什么要用 Multi-Agent？

因为单 Agent 职责不清晰。

Multi-Agent 可以拆分：

- SafetyAgent
- IntentAgent
- PlannerAgent
- RetrievalRouter
- ReflectionAgent

系统更容易扩展和维护。

---

## Q3：Agentic RAG 和普通 RAG 有什么区别？

普通 RAG：

检索一次 -> 生成答案

Agentic RAG：

任务规划 -> 工具检索 -> 结果反思 -> 重新规划

所以更适合复杂问题。

---

## Q4：什么是多跳任务？

例如：

我的订单 O1001 可以退货吗？

需要：

1. 查订单
2. 查售后政策

所以会规划：

```python
["order_task", "policy_task"]