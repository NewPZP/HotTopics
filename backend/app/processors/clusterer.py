# 聚类引擎 — HDBSCAN + LLM标签生成
import logging
import uuid
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


def cluster_articles(articles: list[dict]) -> list[dict]:
    """
    对文章进行聚类。
    优先使用 HDBSCAN + Embedding；如果依赖不可用，回退到基于关键词的简单聚类。
    """
    if not articles:
        return []

    try:
        return _hdbscan_cluster(articles)
    except ImportError:
        logger.warning("HDBSCAN/sklearn 不可用，使用关键词聚类")
    except Exception as e:
        logger.warning(f"HDBSCAN聚类失败: {e}，回退到关键词聚类")

    return _keyword_cluster(articles)


def _hdbscan_cluster(articles: list[dict]) -> list[dict]:
    """基于 HDBSCAN 的语义聚类"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from hdbscan import HDBSCAN

    texts = [f"{a.get('title', '')} {a.get('content', '')[:300]}" for a in articles]
    vectorizer = TfidfVectorizer(max_features=500, stop_words=None)
    vectors = vectorizer.fit_transform(texts)

    clusterer = HDBSCAN(min_cluster_size=2, min_samples=1, metric="euclidean")
    labels = clusterer.fit_predict(vectors.toarray())

    return _build_clusters(articles, labels)


def _keyword_cluster(articles: list[dict]) -> list[dict]:
    """基于关键词的简单聚类（回退方案）"""
    keyword_map = defaultdict(list)
    keyword_rules = {
        "AI": ["AI", "人工智能", "大模型", "芯片", "GPT", "智能"],
        "金融": ["央行", "利率", "银行", "金融", "股市", "股票", "基金"],
        "新能源": ["新能源", "光伏", "电池", "电动汽车", "充电", "风电"],
        "政策": ["政策", "监管", "法规", "政府", "国务院", "改革"],
        "半导体": ["半导体", "芯片", "台积电", "英特尔", "三星", "NVIDIA"],
        "国际": ["美国", "欧盟", "日本", "韩国", "中美", "贸易"],
    }

    for article in articles:
        text = article.get("title", "") + article.get("content", "")
        matched = False
        for category, keywords in keyword_rules.items():
            if any(kw in text for kw in keywords):
                keyword_map[category].append(article)
                matched = True
                break
        if not matched:
            keyword_map["综合"].append(article)

    labels = [-1] * len(articles)
    label_map = {cat: idx for idx, cat in enumerate(keyword_map.keys())}
    for i, article in enumerate(articles):
        text = article.get("title", "") + article.get("content", "")
        for category, keywords in keyword_rules.items():
            if any(kw in text for kw in keywords):
                labels[i] = label_map[category]
                break
        if labels[i] == -1:
            labels[i] = label_map.get("综合", 0)

    return _build_clusters(articles, np.array(labels))


def _build_clusters(articles: list[dict], labels: np.ndarray) -> list[dict]:
    """根据标签组装聚类结果"""
    clusters = []
    unique_labels = set(labels)

    for label in unique_labels:
        if label == -1:
            continue

        cluster_articles = [articles[i] for i, l in enumerate(labels) if l == label]
        if len(cluster_articles) < 2:
            continue

        titles = [a["title"] for a in cluster_articles[:5]]
        cluster_id = f"cluster-{uuid.uuid4().hex[:8]}"

        # 按时间排序取最优
        sorted_articles = sorted(cluster_articles, key=lambda a: a.get("published_at", ""), reverse=True)

        # 过滤乱码标签
        raw_tags = [t for a in cluster_articles for t in a.get("topic_tags", [])]
        clean_tags = list(set(t for t in raw_tags if _valid_cluster_tag(t)))

        clusters.append({
            "cluster_id": cluster_id,
            "topic_label": "",
            "icon": "📌",
            "article_count": len(cluster_articles),
            "time_span": _calc_time_span(cluster_articles),
            "importance": min(5, max(1, len(cluster_articles) // 4)),
            "summary": " → ".join(titles[:3]),
            "tags": clean_tags,
            "articles": cluster_articles,
            "representative": sorted_articles[0] if sorted_articles else None,
            "timeline": [],
        })

    # 按文章数降序
    clusters.sort(key=lambda c: c["article_count"], reverse=True)
    logger.info(f"聚类完成: {len(clusters)} 个簇, 覆盖 {sum(c['article_count'] for c in clusters)} 篇文章")
    return clusters


def _calc_time_span(articles: list[dict]) -> str:
    """计算时间跨度"""
    dates = []
    for a in articles:
        pub = a.get("published_at", "")
        if pub:
            dates.append(pub[:10])
    if not dates:
        return "未知"
    unique_dates = sorted(set(dates))
    if len(unique_dates) == 1:
        return "1天"
    return f"{len(unique_dates)}天"


def _valid_cluster_tag(tag: str) -> bool:
    """过滤乱码标签：排除含 ? 或纯符号的无效标签"""
    if not tag or not isinstance(tag, str):
        return False
    if "?" in tag:
        return False
    import re
    return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]|[a-zA-Z]', tag))
