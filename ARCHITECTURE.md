# 项目架构说明

## 1. 项目整体架构

本项目采用 Multi-Agent + Agentic RAG 架构，模拟电商智能客服系统。

整体流程如下：

```text
用户问题
↓
SafetyAgent：安全检查
↓
IntentAgent：意图识别
↓
PlannerAgent：任务规划
↓
RetrievalRouter：工具路由与检索
↓
ReflectionAgent：证据检查与反思
↓
必要时 Re-plan + Re-retrieve
↓
最终回答