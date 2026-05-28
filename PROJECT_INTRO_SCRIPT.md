# 2 分钟项目介绍稿

## 版本一：正式面试版

这个项目是我做的一个 Multi-Agent + Agentic RAG 电商智能客服系统。

它不是普通的 FAQ 问答系统，也不是简单的单轮 RAG，而是把电商客服流程拆成了多个 Agent 来协作完成。

整体流程是：用户问题先经过 SafetyAgent 做安全检查，然后 IntentAgent 判断用户是在问商品价格、库存、订单还是售后。接着 PlannerAgent 会把问题转换成任务列表，例如价格问题会变成 price_task，订单问题会变成 order_task。

对于复杂问题，比如“我的订单 O1001 里的商品可以退货吗？”，系统会自动识别这是一个多跳问题，需要先查订单，再查售后政策，所以会规划成 order_task + policy_task。

然后 RetrievalRouter 根据任务列表动态调用不同工具，包括商品工具、订单工具和售后政策 RAG 工具。工具返回结果后，ReflectionAgent 会判断当前回答是否有足够证据。如果回答为空、证据不足或者命中失败信号，系统会重新规划任务并再次检索。

另外我还设计了 Memory 机制，用来保存最近一次商品、订单和意图，所以系统可以支持“那退货呢”“那物流呢”这种上下文追问。

最后我用 Streamlit 做了一个网页端 Demo，可以直接展示商品查询、订单查询、售后政策问答、多跳任务和上下文追问能力。

这个项目的核心亮点是：任务规划、工具调用、Reflection 反思重规划和 Memory 上下文追问。

---

## 版本二：更口语化版本

我做的是一个电商智能客服项目，主要想解决普通客服机器人只能单轮问答、不能处理复杂问题的问题。

所以我没有只做一个简单的 RAG，而是设计了一个 Multi-Agent + Agentic RAG 架构。

系统里面有几个 Agent：SafetyAgent 做安全检查，IntentAgent 做意图识别，PlannerAgent 做任务规划，RetrievalRouter 负责调用工具，ReflectionAgent 负责检查回答是否可靠。

比如用户问“我的订单 O1001 里的商品可以退货吗？”，这个问题其实不是简单查售后政策，因为系统得先知道订单里买的是什么商品，再去查对应的售后规则。所以我的 PlannerAgent 会自动把这个问题拆成 order_task 和 policy_task。

然后系统会先查订单，再查售后政策，最后把两个结果融合成回答。

另外系统支持上下文追问。比如用户继续问“那物流呢”，系统会根据 Memory 记住上一轮订单 O1001，然后继续查这个订单的物流。

我还加了 ReflectionAgent，如果工具返回结果不充分，系统会判断证据不足，然后重新规划任务再查一轮。

最后我用 Streamlit 做了网页 Demo，方便直接演示整个流程。

---

## 版本三：30 秒短版

我做了一个基于 Multi-Agent + Agentic RAG 的电商智能客服系统。

系统通过 SafetyAgent、IntentAgent、PlannerAgent、RetrievalRouter 和 ReflectionAgent 实现安全检查、意图识别、任务规划、工具调用和证据反思。

它支持商品价格、库存、订单物流、售后政策问答，也支持“订单里的商品能不能退货”这种多跳问题，会自动拆成订单查询和售后政策查询。

同时系统通过 Memory 支持“那退货呢”“那物流呢”这种上下文追问，并基于 Streamlit 做了网页端 Demo。

---

## 面试演示时一句话开场

老师您好，我这个项目是一个 Multi-Agent + Agentic RAG 电商智能客服系统，重点不是普通问答，而是实现了任务规划、工具调用、证据反思、自动重规划和上下文记忆能力。

---

## 面试演示时一句话结尾

所以这个项目本质上是一个具备 Plan、Retrieve、Reflect、Re-plan 闭环能力的 Agentic RAG 应用，而不是简单的规则客服或单轮 RAG。
