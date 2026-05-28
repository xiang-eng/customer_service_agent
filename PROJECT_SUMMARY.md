# 项目面试包装说明

## 一、项目名称

Multi-Agent + Agentic RAG 电商智能客服系统

---

## 二、简历一句话描述

设计并实现一个基于 Multi-Agent + Agentic RAG 的电商智能客服系统，支持商品价格、库存、订单物流、售后政策问答、多跳任务规划、上下文追问和 Reflection 自动重规划能力，并基于 Streamlit 实现网页端交互 Demo。

---

## 三、简历项目描述

### 版本 1：适合放简历

Multi-Agent + Agentic RAG 电商智能客服系统

- 设计并实现多 Agent 协作架构，包含 SafetyAgent、IntentAgent、PlannerAgent、RetrievalRouter、ReflectionAgent 等核心模块。
- 构建 Agentic RAG 工作流，实现 Plan -> Retrieve -> Reflect -> Re-plan 闭环，支持复杂问题的自动任务拆解与重规划。
- 实现商品库、订单库、售后政策 RAG 多工具动态路由，支持价格查询、库存查询、订单物流查询和售后政策问答。
- 针对“我的订单 O1001 里的商品可以退货吗？”等多跳问题，自动拆分为 order_task + policy_task，并融合多工具结果生成回答。
- 引入 Memory 机制，保存 last_product、last_order、last_intents，实现“那退货呢”“那物流呢”等多轮上下文追问。
- 基于 Streamlit 搭建网页端交互 Demo，支持项目可视化演示与多轮对话测试。

---

### 版本 2：适合 AI 应用方向

基于 Python 实现 Multi-Agent + Agentic RAG 电商智能客服系统，构建 Safety、Intent、Planner、Retrieval、Reflection 多 Agent 协作流程，实现任务规划、工具调用、证据反思、自动重规划和上下文记忆能力。系统支持商品、订单、售后政策等多源数据检索，并通过 Streamlit 提供网页端 Demo 展示。

---

### 版本 3：适合后端 / AI 工程方向

实现电商智能客服系统后端逻辑，完成商品查询、订单查询、售后政策问答等核心业务模块。系统采用 Multi-Agent 架构进行模块解耦，通过 PlannerAgent 进行任务规划，通过 RetrievalRouter 动态调用商品、订单、RAG 工具，并引入 ReflectionAgent 对回答进行证据校验和自动重试，提升系统鲁棒性和可解释性。

---

## 四、项目介绍话术

面试官问：介绍一下你的项目。

可以这样回答：

这个项目是我做的一个 Multi-Agent + Agentic RAG 电商智能客服系统。

它不是普通 FAQ，也不是简单调用大模型回答，而是把客服流程拆成多个 Agent 来协作。

整体流程是：

用户问题先经过 SafetyAgent 做安全检查，然后由 IntentAgent 识别用户是在问价格、库存、订单还是售后。接着 PlannerAgent 会把用户问题转换成任务列表，比如价格问题会变成 price_task，订单问题会变成 order_task。

如果是复杂问题，比如“我的订单 O1001 里的商品可以退货吗”，系统会自动拆成 order_task 和 policy_task，也就是先查订单，再查售后政策。

然后 RetrievalRouter 根据任务列表动态调用商品工具、订单工具或售后 RAG 工具。最后 ReflectionAgent 会检查当前回答是否有证据，如果回答为空、证据不足或者命中失败信号，就会重新规划任务并再次检索。

另外我还加了 Memory 机制，可以支持“那退货呢”“那物流呢”这种上下文追问。最后我用 Streamlit 做了一个网页 Demo，可以直接演示多轮对话效果。

---

## 五、项目核心流程

用户问题
↓
SafetyAgent：安全检查
↓
IntentAgent：意图识别
↓
PlannerAgent：任务规划
↓
RetrievalRouter：动态工具调用
↓
商品工具 / 订单工具 / 售后政策 RAG
↓
ReflectionAgent：证据检查
↓
如果证据不足，自动 Re-plan
↓
最终回答

---

## 六、项目亮点

### 1. Multi-Agent 架构

系统不是一个大函数写到底，而是拆成多个 Agent：

- SafetyAgent：负责安全检查
- IntentAgent：负责意图识别
- PlannerAgent：负责任务规划
- RetrievalRouter：负责工具调用
- ReflectionAgent：负责结果反思

这样每个模块职责清晰，方便调试和扩展。

---

### 2. Agentic RAG 闭环

普通 RAG 通常是：

Retrieve -> Generate

本项目是：

Plan -> Retrieve -> Reflect -> Re-plan

也就是先规划任务，再检索工具，然后反思结果，如果不够再重新规划。

---

### 3. 多跳任务规划

例如用户问：

我的订单 O1001 里的商品可以退货吗？

这个问题需要两个步骤：

1. 查询订单，知道订单里的商品是什么。
2. 查询售后政策，判断是否支持退货。

系统会自动规划为：

["order_task", "policy_task"]

---

### 4. Reflection 反思机制

ReflectionAgent 会判断：

- 回答是否为空
- 证据是否为空
- 是否出现“没有找到相关信息”等失败信号
- 回答是否过短

如果不满足要求，就会重新规划并再次检索。

---

### 5. Memory 上下文追问

系统会保存：

- last_product
- last_order
- last_intents

所以可以支持：

那退货呢？
那物流呢？

这种省略主语的追问。

---

### 6. Streamlit 网页 Demo

项目不只是命令行运行，还实现了网页端交互页面，方便面试或答辩时直接演示。

---

## 七、项目难点

### 难点 1：多 Agent 状态一致性

用户可能先问：

小米 14 有货吗？

然后再问：

我的订单 O1001 里的商品可以退货吗？

这时候系统不能把售后问题错误绑定到小米 14，而应该绑定到订单 O1001 里的商品。

解决方法：

在订单查询完成后，同步更新 memory 中的 last_order 和 last_product，保证后续追问绑定到正确上下文。

---

### 难点 2：短追问理解

用户可能问：

那物流呢？
那退货呢？

这类问题本身没有完整信息。

解决方法：

通过 is_followup_question 判断短追问，再结合 memory 里的 last_order、last_product、last_intents 继承上下文。

---

### 难点 3：工具结果不稳定

RAG 或 LLM 可能失败，或者返回空结果。

解决方法：

加入 ReflectionAgent 做回答校验，如果证据不足则重新规划任务；同时在 executors.py 中加入兜底回答，避免系统崩溃。

---

### 难点 4：多跳问题拆解

复杂问题往往不是单一工具能回答。

解决方法：

PlannerAgent 会根据关键词和意图自动补充任务，比如订单 + 退货问题会自动补充 order_task 和 policy_task。

---

## 八、面试高频问答

### Q1：为什么要用 Multi-Agent？

答：

因为客服系统中不同步骤的职责不同，比如安全检查、意图识别、任务规划、工具调用、结果反思。如果全部写在一个 Agent 或一个函数里，逻辑会非常混乱，也不方便扩展。

拆成 Multi-Agent 后，每个 Agent 职责清楚，系统更容易调试，也更符合真实 Agent 工程的设计方式。

---

### Q2：Agentic RAG 和普通 RAG 有什么区别？

答：

普通 RAG 一般是先检索，再生成：

Retrieve -> Generate

但 Agentic RAG 多了任务规划、工具调用、反思和重规划能力：

Plan -> Retrieve -> Reflect -> Re-plan

所以 Agentic RAG 更适合复杂问题、多跳问题和多工具协作场景。

---

### Q3：你的 ReflectionAgent 具体做了什么？

答：

ReflectionAgent 主要做回答质量检查。

它会判断：

1. answer 是否为空。
2. evidence 是否为空。
3. 回答中是否包含失败信号。
4. 回答是否过短。

如果判断证据不足，就会调用 reflect_and_replan 补充任务，然后重新进入 RetrievalRouter 检索。

---

### Q4：你的多跳任务是怎么实现的？

答：

主要在 PlannerAgent 和 planner_agentic.py 里实现。

例如用户问：

我的订单 O1001 里的商品可以退货吗？

系统会识别到里面既有“订单”，又有“退货”这种售后关键词，所以会规划出两个任务：

order_task
policy_task

然后 RetrievalRouter 会先查订单，再查售后政策，最后把结果拼接成最终回答。

---

### Q5：Memory 是怎么设计的？

答：

Memory 保存最近一次的商品、订单和意图：

last_product
last_order
last_intents

如果用户问“那物流呢”，系统会从 memory 中取出最近订单继续查询。

如果用户问“那退货呢”，系统会从 memory 中取出最近商品或订单里的商品，继续查询售后政策。

---

### Q6：为什么不用完全 LLM Planner？

答：

规则 Planner 更稳定、成本更低、可控性更强。

在这个项目里，我先用规则 Planner 保证系统稳定，同时预留了 LLM Router 接口。后续可以升级成规则 + LLM 混合规划。

---

### Q7：如果 RAG 失败怎么办？

答：

我做了两层处理：

第一层是 ReflectionAgent，如果答案不足，会重新规划任务并再次检索。

第二层是在 execute_policy_task 里加入兜底逻辑，如果 Chroma 或 RAG 报错，会返回本地售后政策模板，保证系统不会崩溃。

---

### Q8：你的项目和普通客服机器人有什么区别？

答：

普通客服机器人一般是 FAQ 或单轮检索问答，用户问一句，系统答一句。

我的系统具备任务规划、工具调用、证据反思、自动重规划和上下文记忆能力，能够处理订单 + 售后这种多跳问题，也能支持“那物流呢”这种多轮追问。

---

### Q9：如果上线，你会怎么优化？

答：

我会从几个方向优化：

1. 接入真实商品库、订单库和售后知识库。
2. RAG 检索增加向量检索和 rerank。
3. 引入真实 LLM Planner 和 Verifier Agent。
4. 增加日志系统和自动化评测集。
5. 使用 FastAPI 封装后端服务。
6. 用 Docker 部署。
7. 增加公网访问 Demo。

---

### Q10：这个项目最大的收获是什么？

答：

最大收获是理解了 Agentic RAG 不只是简单调用大模型，而是要设计完整的任务规划、工具调用、状态管理、证据校验和失败兜底流程。

我也通过这个项目理解了 Multi-Agent 系统中模块解耦、上下文记忆和反思重规划的重要性。

---

## 九、Demo 演示顺序

面试时建议这样演示：

1. 打开 Streamlit 页面。
2. 输入：华为 Mate 60 多少钱？
3. 输入：华为 Mate 60 有货吗？
4. 输入：我的订单 O1001 到哪了？
5. 输入：我的订单 O1001 里的商品可以退货吗？
6. 输入：那退货呢？
7. 输入：那物流呢？

每一步展示的能力：

- 价格查询：商品工具
- 库存查询：商品工具
- 订单查询：订单工具
- 订单 + 退货：多跳任务规划
- 那退货呢：Memory 上下文追问
- 那物流呢：Memory 上下文追问

---

## 十、一句话总结

这个项目是一个基于 Multi-Agent + Agentic RAG 的电商智能客服系统，核心亮点是任务规划、工具调用、Reflection 反思重规划和 Memory 上下文追问。
