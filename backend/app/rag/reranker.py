# 重排序 — 简单 Cross-Encoder 重排
import logging

logger = logging.getLogger(__name__)


def rerank(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    """
    对检索结果重排序。
    优先使用基于相关性的简单重排；后续可接入 Cohere Reranker。
    """
    if not documents:
        return []

    # 简单规则重排：标题匹配得分高于内容匹配
    query_terms = set(query.lower().split())

    for doc in documents:
        title = doc.get("title", "").lower()
        content = doc.get("content", "").lower()

        title_score = sum(1 for t in query_terms if t in title)
        content_score = sum(0.5 for t in query_terms if t in content)
        doc["_rerank_score"] = title_score * 2 + content_score

    documents.sort(key=lambda d: d.get("_rerank_score", 0), reverse=True)
    return documents[:top_k]
