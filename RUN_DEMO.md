# 项目运行说明

## 1. 项目运行环境

推荐环境：

Python 3.11
Conda
Streamlit

---

## 2. 创建 Conda 环境

conda create -n customer python=3.11 -y

激活环境：

conda activate customer

---

## 3. 安装依赖

进入项目目录：

cd C:\Users\Lenovo\Desktop\customer_service_agent

安装依赖：

pip install -r requirements.txt

如果运行时提示缺少 torchvision，执行：

pip install torchvision

---

## 4. 命令行 Demo

运行：

python test_multi_agent.py

会自动测试以下问题：

1. 你好
2. 华为 Mate 60 多少钱？
3. 华为 Mate 60 有货吗？
4. 小米 14 有货吗？
5. 我的订单 O1001 到哪了？
6. 我的订单 O1001 里的商品可以退货吗？
7. 那退货呢？
8. 那物流呢？

---

## 5. Streamlit 网页 Demo

运行：

streamlit run app_streamlit.py

终端出现：

Local URL: http://localhost:8501

打开浏览器访问：

http://localhost:8501

---

## 6. 推荐演示顺序

建议按下面顺序输入：

1. 华为 Mate 60 多少钱？
2. 华为 Mate 60 有货吗？
3. 我的订单 O1001 到哪了？
4. 我的订单 O1001 里的商品可以退货吗？
5. 那退货呢？
6. 那物流呢？

---

## 7. 每个问题展示什么能力

### 问题 1

华为 Mate 60 多少钱？

展示：

商品价格查询

---

### 问题 2

华为 Mate 60 有货吗？

展示：

商品库存查询

---

### 问题 3

我的订单 O1001 到哪了？

展示：

订单查询 + 物流查询

---

### 问题 4

我的订单 O1001 里的商品可以退货吗？

展示：

多跳任务规划
订单查询
售后政策 RAG
工具路由

---

### 问题 5

那退货呢？

展示：

上下文追问
Memory 记忆
售后政策查询

---

### 问题 6

那物流呢？

展示：

上下文追问
Memory 记忆
订单物流查询

---

## 8. 常见问题

### 8.1 提示找不到 app_streamlit.py

说明当前终端目录不对。

请先进入项目目录：

cd C:\Users\Lenovo\Desktop\customer_service_agent

再运行：

streamlit run app_streamlit.py

---

### 8.2 页面能打开，但终端很多 transformers 日志

这是正常现象，不影响项目运行。

只要浏览器页面能正常回答问题，就说明项目成功运行。

---

### 8.3 Chroma 数据库只读报错

项目中已经在 executors.py 里加入售后政策兜底逻辑。

如果 Chroma 或 RAG 出错，会自动返回本地售后政策模板，不会导致页面崩溃。

---

## 9. 项目演示说明词

本项目是一个 Multi-Agent + Agentic RAG 电商智能客服系统。

系统支持商品、库存、订单、售后政策等场景问答。

核心流程是：

SafetyAgent
-> IntentAgent
-> PlannerAgent
-> RetrievalRouter
-> ReflectionAgent

不同于普通 RAG，本项目实现了：

Plan -> Retrieve -> Reflect -> Re-plan

可以处理多跳问题，并支持多轮上下文追问。
