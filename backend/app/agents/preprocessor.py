# PreprocessAgent — 文本清洗与标准化
import logging
from app.agents.state import PlatformState
from app.processors.text_cleaner import clean_article

logger = logging.getLogger(__name__)


async def preprocessor_node(state: PlatformState) -> PlatformState:
    """预处理节点：清洗HTML、标准化文本、语言检测"""
    state["current_step"] = "preprocess"
    state["progress"] = 15.0

    articles = state.get("raw_articles", [])
    if not articles:
        logger.warning("[PreprocessAgent] 无文章需要预处理")
        state["cleaned_articles"] = []
        return state

    logger.info(f"[PreprocessAgent] 开始预处理 {len(articles)} 篇文章")

    cleaned = []
    errors = []

    for article in articles:
        try:
            cleaned_article = clean_article(article)
            cleaned.append(cleaned_article)
        except Exception as e:
            errors.append(f"{article.get('id', 'unknown')}: {str(e)}")

    state["cleaned_articles"] = cleaned
    state["preprocess_errors"] = errors
    state["progress"] = 20.0

    # 持久化清洗后文章到数据库
    if cleaned:
        try:
            from app.repositories.article_repo import ArticleRepo
            ArticleRepo.upsert_processed_articles(cleaned)
        except Exception as e:
            logger.warning(f"[PreprocessAgent] DB 持久化失败: {e}")

    logger.info(f"[PreprocessAgent] 预处理完成: {len(cleaned)} 篇, 错误 {len(errors)}")
    return state
