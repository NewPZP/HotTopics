# DedupAgent — 去重检测
import logging
from app.agents.state import PlatformState
from app.processors.deduplicator import exact_dedup, simhash_dedup

logger = logging.getLogger(__name__)


async def dedup_node(state: PlatformState) -> PlatformState:
    """去重节点：精确去重 + SimHash 近似去重"""
    state["current_step"] = "dedup"
    state["progress"] = 25.0

    articles = state.get("cleaned_articles", [])
    if not articles:
        logger.warning("[DedupAgent] 无文章需要去重")
        state["unique_articles"] = []
        state["duplicates_removed"] = 0
        return state

    total = len(articles)
    logger.info(f"[DedupAgent] 开始去重 {total} 篇文章")

    # 第一层：精确去重
    articles, removed1 = exact_dedup(articles)

    # 第二层：近似去重
    articles, removed2 = simhash_dedup(articles)

    total_removed = removed1 + removed2
    # 过滤掉标记为重复的文章
    unique = [a for a in articles if not a.get("is_duplicate")]

    state["unique_articles"] = unique
    state["duplicates_removed"] = total_removed
    state["dedup_details"] = {
        "original": total,
        "exact_removed": removed1,
        "simhash_removed": removed2,
        "remaining": len(unique),
    }
    state["progress"] = 35.0

    logger.info(f"[DedupAgent] 去重完成: 移除 {total_removed} 篇, 保留 {len(unique)} 篇")
    return state
