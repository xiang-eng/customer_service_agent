# =====================================
# agentic_rag_policy.py
# 作用：
# 在现有 Full RAG 基础上增加 Agentic RAG 能力
#
# 当前流程：
# 1. Query Rewrite：把口语问题改写成适合检索的问题
# 2. Hybrid Retrieval：调用 full_rag_policy 的 Hybrid Search
# 3. Context Judge：判断检索结果是否足够相关
# 4. Answer Generation：基于检索上下文生成回答
# 5. Fallback：失败时回退政策片段或人工客服提示
# =====================================

# 导入正则，用于简单文本处理
import re

# 从现有 full_rag_policy 复用已有能力
from full_rag_policy import (
    build_policy_vector_db,
    retrieve_policy_chunks,
    build_rag_prompt,
    get_llm_client,
)


# =====================================
# Agentic RAG 缓存
# =====================================
# key：用户原始问题
# value：最终回答
#
# 作用：
# 相同售后问题第二次直接返回，减少检索和 LLM 调用
agentic_rag_cache = {}


def rewrite_policy_query(question):
    """
    Query Rewrite：把用户问题改写成更适合售后检索的问题

    为什么要做？
    用户经常会说：
    - 坏了咋办
    - 能处理吗
    - 能不能售后
    - 这个能换不

    这些说法比较口语，直接检索可能不稳定。
    所以这里把它们改写成更标准的售后检索 query。

    当前版本用规则改写，优点是稳定、快、不依赖 LLM。
    """

    # 去掉前后空格
    q = question.strip()

    # 用一个列表保存“增强后的检索关键词”
    keywords = []

    # 保留原始问题
    keywords.append(q)

    # 如果用户问退货
    if any(word in q for word in ["退", "退货", "退款", "能不能退", "可以退"]):
        keywords.append("未拆封 7天无理由退货 已拆封 不支持无理由退货")

    # 如果用户问换货
    if any(word in q for word in ["换", "换货", "能不能换", "可以换"]):
        keywords.append("质量问题 15天 换货")

    # 如果用户说坏了
    if any(word in q for word in ["坏", "坏了", "坏掉", "故障", "不能用"]):
        keywords.append("商品损坏 质量问题 换货 保修 人为损坏")

    # 如果用户问保修
    if any(word in q for word in ["保修", "维修", "修"]):
        keywords.append("智能家居商品 保修期 1年 人为损坏 不在保修范围")

    # 如果用户问售后但没说清楚
    if any(word in q for word in ["售后", "处理", "怎么办", "咋办"]):
        keywords.append("售后政策 退货 换货 保修 质量问题")

    # 把增强后的关键词拼起来
    rewritten = " ".join(keywords)

    print(f"【Agentic RAG】Query Rewrite：{rewritten}")

    return rewritten


def judge_context_relevance(question, chunks):
    """
    Context Judge：判断检索到的内容是否足够相关

    为什么要做？
    RAG 有时候会检索到不太相关的内容。
    如果内容明显不相关，就不应该强行让 LLM 回答。

    当前版本是轻量规则判断：
    只要检索内容里命中售后关键词，就认为可用。
    """

    if not chunks:
        return False

    # 把所有 chunk 拼成一个大文本
    context = "\n".join(chunks)

    # 售后相关关键词
    important_words = [
        "退货",
        "换货",
        "保修",
        "质量问题",
        "人为损坏",
        "无理由",
        "15 天",
        "7 天",
    ]

    # 只要命中任意一个关键词，就认为上下文可用
    for word in important_words:
        if word in context:
            print("【Agentic RAG】Context Judge：检索内容相关")
            return True

    print("【Agentic RAG】Context Judge：检索内容相关性不足")
    return False


def generate_answer_with_context(question, chunks):
    """
    基于检索结果生成最终回答

    这里仍然调用百炼 LLM。
    如果 LLM 失败，外层函数会负责 fallback。
    """

    # 构造 RAG Prompt
    prompt = build_rag_prompt(question, chunks)

    # 获取 LLM 客户端
    client = get_llm_client()

    # 调用 LLM
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {
                "role": "system",
                "content": "你是严格基于售后政策回答问题的客服助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    # 返回模型生成内容
    return completion.choices[0].message.content.strip()


def answer_policy_with_agentic_rag(question, top_k=3):
    """
    Agentic RAG 对外主函数

    输入：
    - 用户原始售后问题

    输出：
    - 售后回答
    """

    # =========================
    # 1. 查缓存
    # =========================
    cache_key = question.strip()

    if cache_key in agentic_rag_cache:
        print("【Agentic RAG缓存命中】直接返回缓存回答")
        return agentic_rag_cache[cache_key]

    # =========================
    # 2. 确保向量库存在
    # =========================
    build_policy_vector_db(force_rebuild=False)

    # =========================
    # 3. Query Rewrite
    # =========================
    rewritten_query = rewrite_policy_query(question)

    # =========================
    # 4. Hybrid Retrieval
    # =========================
    chunks = retrieve_policy_chunks(
        rewritten_query,
        top_k=top_k
    )

    print("【Agentic RAG】检索到的政策片段：")
    for chunk in chunks:
        print(f"- {chunk}")

    # =========================
    # 5. Context Judge
    # =========================
    is_relevant = judge_context_relevance(question, chunks)

    if not is_relevant:
        answer = "暂时没有找到明确售后政策，请联系人工客服确认。"
        agentic_rag_cache[cache_key] = answer
        return answer

    # =========================
    # 6. Answer Generation
    # =========================
    try:
        answer = generate_answer_with_context(
            question,
            chunks
        )

        agentic_rag_cache[cache_key] = answer

        print("【Agentic RAG缓存写入】已缓存回答")

        return answer

    except Exception as e:
        print(f"【Agentic RAG生成失败】{e}")

        # =========================
        # 7. Fallback
        # =========================
        fallback_answer = (
            "根据我们的售后政策：\n"
            + "\n".join(chunks)
        )

        agentic_rag_cache[cache_key] = fallback_answer

        print("【Agentic RAG缓存写入】已缓存回退回答")

        return fallback_answer