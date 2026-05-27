import math


def text_to_vector(text):
    """
    把一句话转成“词频向量”

    为了简单，这里不做中文分词，
    直接按“字”统计频次。
    """

    words = list(text)
    vector = {}

    for w in words:
        vector[w] = vector.get(w, 0) + 1

    return vector


def cosine_similarity(vec1, vec2):
    """
    计算两个向量的余弦相似度
    数值越大，代表越相似
    """

    common_keys = set(vec1.keys()) & set(vec2.keys())

    dot_product = sum(vec1[k] * vec2[k] for k in common_keys)

    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot_product / (norm1 * norm2)


def build_policy_chunks(policy_text):
    """
    把完整售后政策切成一条一条的“检索片段”

    同时过滤掉标题行：
    例如“售后政策：”
    """

    lines = policy_text.splitlines()
    chunks = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # 跳过标题
        if line in ["售后政策：", "售后政策"]:
            continue

        chunks.append(line)

    return chunks


def keyword_bonus(question, chunk):
    """
    给检索结果加“业务规则分”

    目的：
    单纯靠余弦相似度时，有些不够相关的政策也会排上来。
    所以这里人为加一点“关键词奖励”，让结果更贴近业务语义。
    """

    bonus = 0

    # 统一转小写（虽然中文影响不大，但写法更规范）
    q = question.lower()
    c = chunk.lower()

    # 如果用户在问“退”
    if "退" in q:
        if "退货" in c or "无理由" in c:
            bonus += 0.6

    # 如果用户在问“换”
    if "换" in q:
        if "换货" in c or "质量问题" in c:
            bonus += 0.6

    # 如果用户在问“坏了”
    if "坏" in q:
        if "人为损坏" in c or "质量问题" in c or "保修" in c:
            bonus += 0.6

    # 如果问题里明确提“保修”
    if "保修" in q:
        if "保修" in c:
            bonus += 0.6

    return bonus


def search_policy_rag(question, policy_text, top_k=2):
    """
    核心函数：简化版 RAG 检索

    参数：
    - question：用户问题
    - policy_text：完整售后政策文本
    - top_k：返回最相关的几条

    返回：
    - 拼接后的最相关政策文本
    """

    # 1. 把政策拆成片段
    chunks = build_policy_chunks(policy_text)

    # 2. 把问题转成向量
    q_vec = text_to_vector(question)

    scored = []

    # 3. 每条政策都算一个得分
    for chunk in chunks:
        c_vec = text_to_vector(chunk)

        # 基础语义相似度
        sim = cosine_similarity(q_vec, c_vec)

        # 关键词奖励
        bonus = keyword_bonus(question, chunk)

        # 最终分数 = 相似度 + 奖励
        final_score = sim + bonus

        scored.append((chunk, final_score))

    # 4. 按得分从高到低排序
    scored.sort(key=lambda x: x[1], reverse=True)

    # 5. 取前 top_k 条
    top_chunks = [c[0] for c in scored[:top_k]]

    # 6. 去重，避免重复
    unique_chunks = []
    for chunk in top_chunks:
        if chunk not in unique_chunks:
            unique_chunks.append(chunk)

    # 7. 拼接返回
    return "\n".join(unique_chunks)