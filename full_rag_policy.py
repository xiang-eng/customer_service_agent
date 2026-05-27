# =====================================
# full_rag_policy.py
# 作用：
# 实现完整版售后政策 RAG
#
# 当前版本包含：
# 1. 读取 policy.txt
# 2. 切分成 chunk
# 3. 用 embedding 模型向量化
# 4. 存入 Chroma 向量数据库
# 5. Dense Retrieval：向量检索
# 6. Sparse Retrieval：BM25 关键词检索
# 7. Hybrid Search：向量分数 + BM25分数 + 业务关键词加权
# 8. 把检索结果作为 context
# 9. 调用 LLM 基于 context 生成回答
# 10. LLM 失败时回退检索片段
# 11. RAG 回答缓存
# =====================================
'''为什么要加 BM25？
    - 向量检索擅长语义相似
    - BM25 擅长关键词匹配
    - 两者结合就是 Hybrid Search
    """'''

import os

# Chroma：本地向量数据库
import chromadb

# sentence-transformers：本地 embedding 模型
from sentence_transformers import SentenceTransformer

# rank_bm25：BM25 关键词检索
from rank_bm25 import BM25Okapi

# OpenAI 兼容客户端，用来调用阿里云百炼
from openai import OpenAI

# dotenv：读取 .env 文件里的 API Key
from dotenv import load_dotenv


# =====================================
# 一、读取环境变量
# =====================================
load_dotenv()


# =====================================
# 二、基础路径配置
# =====================================

# 当前项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 售后政策文件路径
POLICY_FILE = os.path.join(BASE_DIR, "data", "policy.txt")

# Chroma 向量库存储目录
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_policy_db")

# Chroma collection 名称
COLLECTION_NAME = "policy_chunks"


# =====================================
# 三、初始化 embedding 模型
# =====================================
# 这个模型支持多语言，适合中文短文本检索的入门版本。
# 第一次运行会下载模型，后面会复用本地缓存。
embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# =====================================
# 四、Full RAG 回答缓存
# =====================================
# key：用户问题
# value：RAG 最终回答
#
# 作用：
# - 第一次问售后问题时，正常走检索 + LLM生成
# - 第二次问相同问题时，直接返回缓存结果
# - 减少重复大模型调用，降低响应耗时
rag_cache = {}


# =====================================
# 五、BM25 检索器缓存
# =====================================
# bm25_retriever：
# - 保存 BM25 检索器对象
#
# bm25_chunks：
# - 保存参与 BM25 检索的政策文本片段
#
# 为什么要缓存？
# - BM25 初始化不需要每次问题都重新做
# - 初始化一次后重复使用即可
bm25_retriever = None
bm25_chunks = None


def get_llm_client():
    """
    创建百炼 LLM 客户端

    用途：
    - 检索到政策片段后
    - 调用 LLM 基于这些片段生成自然语言回答
    """

    # 从 .env 中读取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")

    # 如果没有配置，就抛出错误
    if not api_key:
        raise ValueError("未找到 DASHSCOPE_API_KEY，请检查 .env 文件")

    # 创建 OpenAI 兼容客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=10.0,
    )

    return client


def load_policy_text():
    """
    读取完整售后政策文本

    返回：
    - policy.txt 文件中的全部内容
    """

    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return f.read()


def split_policy_to_chunks(policy_text):
    """
    把售后政策切分成多个 chunk

    当前 policy.txt 比较短，所以按行切分。

    例如原始文本：
    售后政策：
    1. 未拆封商品支持 7 天无理由退货。
    2. 已拆封但无质量问题的商品，不支持无理由退货。

    切分后：
    [
        "1. 未拆封商品支持 7 天无理由退货。",
        "2. 已拆封但无质量问题的商品，不支持无理由退货。"
    ]
    """

    # 按行切分
    lines = policy_text.splitlines()

    chunks = []

    for line in lines:
        # 去掉每行前后空格
        line = line.strip()

        # 跳过空行
        if not line:
            continue

        # 跳过标题行
        if line in ["售后政策：", "售后政策"]:
            continue

        # 保存真正的政策条目
        chunks.append(line)

    return chunks


def get_chroma_collection():
    """
    获取 Chroma collection

    collection 可以理解成“向量表”。
    里面保存：
    - chunk 文本
    - chunk 向量
    - id
    - metadata
    """

    # PersistentClient 表示持久化存储
    # 数据会保存在 chroma_policy_db 目录中
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # 获取或创建 collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def build_policy_vector_db(force_rebuild=False):
    """
    构建售后政策向量库

    参数：
    - force_rebuild=True：
      强制删除旧数据并重新构建

    - force_rebuild=False：
      如果已经有向量库，就直接复用
    """

    # 获取 Chroma collection
    collection = get_chroma_collection()

    # 查看当前 collection 中已有多少条
    existing_count = collection.count()

    # 如果已经存在，并且不强制重建，就直接返回
    if existing_count > 0 and not force_rebuild:
        # 不打印，避免主系统每次问售后都刷屏
        # print(f"售后政策向量库已存在，共 {existing_count} 条，无需重建。")
        return

    # 如果强制重建，并且原来有数据，就先删除
    if existing_count > 0:
        old_items = collection.get()
        old_ids = old_items.get("ids", [])

        if old_ids:
            collection.delete(ids=old_ids)

    # 读取政策文本
    policy_text = load_policy_text()

    # 切分成 chunk
    chunks = split_policy_to_chunks(policy_text)

    # 给每个 chunk 一个唯一 id
    ids = [f"policy_{i}" for i in range(len(chunks))]

    # 生成向量
    # embeddings 是二维列表：
    # [
    #   [0.1, 0.2, ...],
    #   [0.3, 0.4, ...]
    # ]
    embeddings = embedding_model.encode(chunks).tolist()

    # 写入 Chroma
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"source": "policy.txt"} for _ in chunks]
    )

    print(f"售后政策向量库构建完成，共写入 {len(chunks)} 条。")


def build_bm25():
    """
    构建 BM25 检索器

    BM25 是一种关键词检索算法。
    它更擅长处理精确关键词，比如：
    - 退货
    - 换货
    - 保修
    - 人为损坏

    为什么要加 BM25？
    - 向量检索擅长语义相似
    - BM25 擅长关键词匹配
    - 两者结合就是 Hybrid Search
    """

    global bm25_retriever
    global bm25_chunks

    # 如果已经初始化过，就不重复构建
    if bm25_retriever is not None:
        return

    # 读取政策文本
    policy_text = load_policy_text()

    # 切分政策 chunk
    chunks = split_policy_to_chunks(policy_text)

    # 中文这里为了简单，按“字”切分
    # 例如：
    # "可以换吗" -> ["可", "以", "换", "吗"]
    #
    # 更高级版本可以用 jieba 分词
    tokenized_chunks = []

    for chunk in chunks:
        tokenized_chunks.append(list(chunk))

    # 创建 BM25 检索器
    bm25_retriever = BM25Okapi(tokenized_chunks)

    # 保存 chunk
    bm25_chunks = chunks

    print("BM25 检索器初始化完成")


def bm25_retrieve(question, top_k=3):
    """
    使用 BM25 做关键词检索

    参数：
    - question：用户问题
    - top_k：返回前几条

    返回：
    - BM25 检索出的政策片段列表
    """

    # 确保 BM25 已经初始化
    build_bm25()

    # 用户问题同样按字切分
    query_tokens = list(question)

    # 计算每个 chunk 的 BM25 分数
    scores = bm25_retriever.get_scores(query_tokens)

    # 把 chunk 和分数配对
    scored = list(zip(bm25_chunks, scores))

    # 按分数从高到低排序
    scored.sort(key=lambda x: x[1], reverse=True)

    # 取前 top_k 条
    top_chunks = [item[0] for item in scored[:top_k]]

    return top_chunks


def keyword_bonus(question, chunk):
    """
    业务关键词加权

    为什么需要它？
    因为短中文问题很容易让 embedding 检索不稳定。
    例如：
    “可以换吗”
    向量检索不一定能稳定召回“换货”政策。

    所以这里加一点业务规则：
    - 问退 → 退货/无理由加分
    - 问换 → 换货/质量问题加分
    - 问坏 → 质量问题/人为损坏/保修加分

    注意：
    这不是替代 RAG，而是对检索结果做 rerank。
    """

    bonus = 0.0

    q = question
    c = chunk

    # 用户问退货
    if "退" in q:
        if "退货" in c or "无理由" in c:
            bonus += 1.0

    # 用户问换货
    if "换" in q:
        if "换货" in c or "质量问题" in c:
            bonus += 1.2

    # 用户问坏了
    if "坏" in q:
        if "质量问题" in c:
            bonus += 1.2
        if "人为损坏" in c:
            bonus += 1.0
        if "保修" in c:
            bonus += 0.8

    # 用户问保修
    if "保修" in q:
        if "保修" in c:
            bonus += 1.2
        if "人为损坏" in c:
            bonus += 0.8

    # 用户问质量问题
    if "质量" in q:
        if "质量问题" in c or "换货" in c:
            bonus += 1.2

    return bonus


def retrieve_policy_chunks(question, top_k=3):
    """
    Hybrid Search 检索政策片段

    当前检索流程：
    1. Dense Retrieval：
       用 embedding + Chroma 做向量检索

    2. Sparse Retrieval：
       用 BM25 做关键词检索

    3. Rerank / Late Fusion：
       把向量分数、BM25 排名分、业务关键词加权融合起来

    参数：
    - question：用户问题
    - top_k：最终返回前几条政策

    返回：
    - top_chunks：融合排序后的政策片段
    """

    # =====================================
    # 1. Dense Retrieval：向量检索
    # =====================================

    collection = get_chroma_collection()

    # 用户问题向量化
    query_embedding = embedding_model.encode([question]).tolist()[0]

    # 先从 Chroma 中多召回几条
    # 因为后面还要和 BM25 融合排序
    dense_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "distances"]
    )

    dense_docs = dense_results.get("documents", [[]])[0]
    dense_distances = dense_results.get("distances", [[]])[0]

    # dense_scores 保存向量检索分数
    # key：chunk 文本
    # value：分数
    dense_scores = {}

    for doc, distance in zip(dense_docs, dense_distances):
        # Chroma 返回的是 distance
        # distance 越小表示越相似
        #
        # 这里转成 similarity：
        # distance = 0 → score = 1
        # distance 越大 → score 越小
        vector_score = 1 / (1 + distance)

        # 加上业务关键词奖励
        bonus = keyword_bonus(question, doc)

        # 最终 dense 侧分数
        dense_scores[doc] = vector_score + bonus

    # =====================================
    # 2. Sparse Retrieval：BM25 检索
    # =====================================

    bm25_docs = bm25_retrieve(
        question,
        top_k=5
    )

    # =====================================
    # 3. Late Fusion：融合排序
    # =====================================

    # fused 用来融合两路召回结果
    # key：chunk 文本
    # value：融合分数
    fused = {}

    # 先加入 dense 结果
    for doc, score in dense_scores.items():
        fused[doc] = score

    # 再加入 BM25 结果
    for rank, doc in enumerate(bm25_docs):
        # BM25 这里使用排名加权：
        # 第 1 名：+1.0
        # 第 2 名：+0.5
        # 第 3 名：+0.333
        bm25_bonus = 1 / (rank + 1)

        if doc not in fused:
            fused[doc] = 0.0

        fused[doc] += bm25_bonus

    # =====================================
    # 4. 最终排序
    # =====================================

    ranked = sorted(
        fused.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # 取前 top_k 条
    top_chunks = [item[0] for item in ranked[:top_k]]

    return top_chunks


def build_rag_prompt(question, context_chunks):
    """
    构造 RAG 提示词

    核心要求：
    LLM 只能基于检索到的政策回答。
    """

    # 把检索到的政策片段拼成上下文
    context = "\n".join(context_chunks)

    return f"""
你是一个电商售后客服助手。
请只根据【售后政策内容】回答用户问题。

严格要求：
1. 只能基于售后政策内容回答
2. 不要编造政策里没有的信息
3. 如果政策内容不足以回答，就说“暂时没有找到明确政策，请联系人工客服确认”
4. 回答要简洁、清楚、口语自然

【售后政策内容】
{context}

【用户问题】
{question}

请输出最终回答：
""".strip()


def answer_policy_with_full_rag(question, top_k=3):
    """
    完整版 RAG 对外主函数

    输入：
    - 用户售后问题

    输出：
    - LLM 基于检索结果生成的回答
    - 如果 LLM 失败，就回退为检索片段

    当前包含：
    - Hybrid Search 检索
    - LLM 生成
    - 失败回退
    - RAG 缓存
    """

    # =====================================
    # 1. 先查 RAG 缓存
    # =====================================
    cache_key = question.strip()

    if cache_key in rag_cache:
        print("【RAG缓存命中】直接返回缓存回答")
        return rag_cache[cache_key]

    # =====================================
    # 2. 确保向量库存在
    # =====================================
    build_policy_vector_db(force_rebuild=False)

    # =====================================
    # 3. Hybrid Search 检索相关政策
    # =====================================
    chunks = retrieve_policy_chunks(
        question,
        top_k=top_k
    )

    # 如果没有检索结果，直接兜底
    if not chunks:
        return "暂时没有找到相关售后政策，请联系人工客服确认。"

    # =====================================
    # 4. 构造 RAG Prompt
    # =====================================
    prompt = build_rag_prompt(
        question,
        chunks
    )

    # =====================================
    # 5. 调用 LLM 生成回答
    # =====================================
    try:
        client = get_llm_client()

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": "你是严格基于检索内容回答问题的售后客服。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        answer = completion.choices[0].message.content.strip()

        # 写入缓存
        rag_cache[cache_key] = answer

        print("【RAG缓存写入】已缓存回答")

        return answer

    except Exception as e:
        print(f"【Full RAG 回答生成失败】{e}")

        # =====================================
        # 6. LLM 失败时，回退到检索片段
        # =====================================
        fallback_answer = (
            "根据我们的售后政策：\n"
            + "\n".join(chunks)
        )

        # 回退结果也缓存
        rag_cache[cache_key] = fallback_answer

        print("【RAG缓存写入】已缓存回退回答")

        return fallback_answer