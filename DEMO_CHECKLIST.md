# Demo 演示清单

## 1. 启动项目

进入项目目录：

cd C:\Users\Lenovo\Desktop\customer_service_agent

激活环境：

conda activate customer

启动 Streamlit：

streamlit run app_streamlit.py

浏览器访问：

http://localhost:8501

---

## 2. 演示顺序

建议按照下面顺序演示：

### 第一步：商品价格查询

输入：

华为 Mate 60 多少钱？

展示能力：

- IntentAgent 识别价格查询
- PlannerAgent 规划 price_task
- RetrievalRouter 调用商品工具
- 返回商品价格

---

### 第二步：商品库存查询

输入：

华为 Mate 60 有货吗？

展示能力：

- IntentAgent 识别库存查询
- PlannerAgent 规划 stock_task
- RetrievalRouter 调用库存工具
- 返回库存数量

---

### 第三步：缺货商品查询

输入：

小米 14 有货吗？

展示能力：

- 商品库存查询
- 缺货状态识别

---

### 第四步：订单物流查询

输入：

我的订单 O1001 到哪了？

展示能力：

- IntentAgent 识别订单查询
- PlannerAgent 规划 order_task
- RetrievalRouter 调用订单工具
- 返回订单状态和物流信息
- Memory 记录 last_order

---

### 第五步：多跳售后问题

输入：

我的订单 O1001 里的商品可以退货吗？

展示能力：

- 多跳任务规划
- 自动拆分 order_task + policy_task
- 先查订单
- 再查售后政策
- 融合多个工具结果
- ReflectionAgent 判断证据是否充分

---

### 第六步：上下文追问退货

输入：

那退货呢？

展示能力：

- 短追问识别
- Memory 继承上一轮商品或订单上下文
- 继续调用售后政策工具

---

### 第七步：上下文追问物流

输入：

那物流呢？

展示能力：

- 短追问识别
- Memory 继承上一轮订单 O1001
- 继续查询订单物流信息

---

## 3. 演示时重点讲什么

演示时不要只说“这是客服系统”。

重点说：

这个项目的核心是 Agentic RAG 工作流。

普通 RAG 是：

Retrieve -> Generate

本项目是：

Plan -> Retrieve -> Reflect -> Re-plan

系统能完成：

1. 意图识别
2. 任务规划
3. 工具调用
4. 多跳任务拆解
5. 证据反思
6. 上下文记忆
7. 多轮追问

---

## 4. 面试讲解重点

### 项目不是普通问答

它不是用户问一句，系统简单回答一句。

它会先判断用户意图，再规划任务，再调用不同工具。

---

### 项目支持多工具协作

系统中有：

- 商品工具
- 订单工具
- 售后政策 RAG 工具

RetrievalRouter 根据任务列表动态调用工具。

---

### 项目支持多跳任务

例如：

我的订单 O1001 里的商品可以退货吗？

这个问题需要：

1. 查订单，知道订单里的商品。
2. 查售后政策，判断是否能退货。

所以 PlannerAgent 会自动拆成：

order_task + policy_task

---

### 项目支持 Reflection

如果回答为空、证据不足、命中失败信号，ReflectionAgent 会触发重新规划。

---

### 项目支持 Memory

Memory 保存：

- last_product
- last_order
- last_intents

所以能处理：

那退货呢？
那物流呢？

这种不完整问题。

---

## 5. 一句话总结

这是一个基于 Multi-Agent + Agentic RAG 的电商智能客服系统，核心亮点是任务规划、工具调用、Reflection 反思重规划和 Memory 上下文追问。
