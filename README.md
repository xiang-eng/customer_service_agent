# 🚀 Multi-Agent + Agentic RAG 电商智能客服系统

<p align="center">

一个具备任务规划、工具调用、自反思能力的智能客服 Agent 系统

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-orange)
![Agentic-RAG](https://img.shields.io/badge/Agentic-RAG-green)
![SQLite](https://img.shields.io/badge/SQLite-lightgrey)

</p>

---

# 一、项目简介

这是一个模拟真实电商场景的智能客服 Agent 项目。

支持：

- 商品价格查询
- 商品库存查询
- 订单物流查询
- 售后政策问答（RAG）
- 多轮上下文追问
- 多跳任务拆解
- Reflection 自反思补查
- Multi-Agent 协作

不是传统 FAQ 机器人：

```text
用户问题
→ 匹配规则
→ 返回固定答案
```

而是升级成：

```text
理解问题
→ 任务规划
→ 调用工具
→ 检索证据
→ 自反思补查
→ 最终回答
```

---

# 二、项目一步步怎么来的（演进过程）

这个项目不是一次写成的，是逐步升级的：

---

## 第一阶段：规则客服

最开始只是：

```text
if 用户问价格:
   查价格

if 用户问订单:
   查订单
```

只能处理简单问题。

---

## 第二阶段：工作流 Agent

升级成：

```text
意图识别
→ 任务规划
→ 执行器
```

比如：

```text
小米音箱多少钱？订单在哪？
```

能拆成两个任务处理。

---

## 第三阶段：加入数据库

把写死的数据升级成：

- 商品数据库（SQLite）

- 订单数据库（SQLite）

更像真实系统。

---

## 第四阶段：升级 RAG

售后政策不写死：

```text
问题
→ 检索政策
→ 生成回答
```

---

## 第五阶段：升级 Agentic RAG

加入：

```text
Query Rewrite
Hybrid Retrieval
Reflection
Re-plan
```

形成闭环：

```text
规划
→ 检索
→ 反思
→ 重规划
```

---

## 第六阶段：升级 Multi-Agent

拆成多个 Agent：

```text
CoordinatorAgent
├── SafetyAgent
├── IntentAgent
├── PlannerAgent
├── RetrievalRouter
└── ReflectionAgent
```

这就是最终版。

---

# 三、系统架构

## Agent 架构

```text
CoordinatorAgent
├── SafetyAgent
├── IntentAgent
├── PlannerAgent
├── RetrievalRouter
└── ReflectionAgent
```

---

## 每个 Agent 干什么

---

### SafetyAgent

负责安全检查。

比如：

- 非业务问题拦截

- 敏感问题过滤

---

### IntentAgent

判断用户问什么：

```text
价格
库存
订单
售后
```

---

### PlannerAgent

负责拆任务。

例如：

```text
订单里的商品可以退货吗
```

拆成：

```text
查订单

查售后政策
```

---

### RetrievalRouter

决定调哪个工具：

```text
价格工具

库存工具

订单工具

RAG工具
```

---

### ReflectionAgent

负责检查：

```text
证据够不够？

答案完整吗？
```

不够就补查。

---

# 四、系统工作流

```text
用户问题
↓

安全检查

↓

意图识别

↓

任务规划

↓

工具路由

↓

证据反思

↓

必要时重新规划

↓

最终回答
```

---

## 闭环

```text
Plan

↓

Retrieve

↓

Reflect

↓

Re-plan
```

这是 Agentic RAG 核心。

---

# 五、核心功能

---

## 1 商品咨询

支持：

- 商品价格

- 商品库存

示例：

```text
用户：
小米智能音箱多少钱

客服：
199元
```

---

## 2 订单查询

支持：

- 发货状态

- 物流状态

示例：

```text
订单 O1001 到哪了
```

---

## 3 售后问答（RAG）

支持：

```text
退货

换货

保修
```

示例：

```text
可以换吗
```

---

## 4 多轮追问

支持：

```text
那物流呢

那退货呢
```

系统能继承上下文。

---

## 5 多跳问题

例如：

```text
订单里的商品可以退货吗
```

自动拆：

```text
order_task

policy_task
```

---

# 六、Agentic RAG 设计

---

## Query Rewrite

用户说：

```text
坏了咋整
```

系统会改写成：

```text
质量问题
换货
保修
人为损坏
```

方便检索。

---

## Hybrid Retrieval

不是只用向量检索。

而是：

```text
向量检索

+ BM25

+ 关键词重排
```

为什么？

因为：

```text
可以换吗
```

这种问题很短。

纯向量容易召回不好。

BM25 能补。

---

## Reflection

如果检索证据不足：

```text
补任务

重新检索
```

---

## Fallback

如果 LLM 超时：

直接返回检索结果。

系统不崩。

---

# 七、Memory

保存：

```text
last_product

last_order

last_intents
```

支持：

```text
那库存呢
```

这种追问。

---

# 八、缓存优化

做了三层缓存：

---

## Router缓存

缓存任务规划。

---

## 回答缓存

重复问题直接返回。

---

## RAG缓存

第一次：

10秒

第二次：

毫秒级

---

# 九、技术栈

## 基础

- Python

- SQLite

- Streamlit

---

## Agent

- Multi-Agent

- ReAct

- LangGraph 风格工作流

---

## RAG

- BM25

- Chroma

- SentenceTransformer

---

## 大模型

- Qwen

---

# 十、项目目录

```text
customer_service_agent/

├── main_v06.py
├── main_agentic.py

├── multi_agent.py
├── planner_agentic.py
├── retrieval_router.py
├── reflection_agent.py

├── executors.py
├── db_tools.py
├── memory.py

├── agentic_rag_policy.py
├── full_rag_policy.py

└── app.py
```

---

# 十一、运行方式

初始化数据库：

```bash
python init_db.py
```

启动：

```bash
python main_agentic.py
```

网页 Demo：

```bash
streamlit run app.py
```

---

# 十二、测试问题

```text
小米智能音箱多少钱

华为门铃还有货吗

订单 O1001 到哪了

订单 O1001 里的商品可以退货吗

那物流呢

可以换吗
```

---

# 十三、项目亮点

---

## 亮点1

从普通客服升级到 Agentic RAG。

---

## 亮点2

Multi-Agent 协作。

---

## 亮点3

多工具联合推理：

```text
商品库

订单库

政策RAG
```

---

## 亮点4

Reflection 自反思。

---

## 亮点5

上下文 Memory。

---

# 十四、简历写法

项目名称：

```text
Multi-Agent + Agentic RAG 电商智能客服系统
```

---

项目描述：

```text
设计并实现 Multi-Agent + Agentic RAG 电商智能客服系统，构建 Safety/Intent/Planner/Retrieval/Reflection 多Agent协作框架，实现多跳任务规划、工具动态路由、证据反思重规划与上下文追问能力。
```

---

# 十五、一句话介绍项目

```text
这是一个从规则客服逐步升级到具备任务规划、工具调用、自反思能力的 Multi-Agent Agentic RAG 智能客服系统。
```

---

# 十六、未来还能升级

可以继续做：

- Critic Agent

- Graph Planner

- 长期记忆

- 服务化部署

---