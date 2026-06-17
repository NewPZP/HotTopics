# ComposeAgent — 日报组装
import logging
import uuid
from datetime import datetime
from app.agents.state import PlatformState
from app.generators.summarizer import call_llm_async
from app.generators.prompts import BRIEF_COMPOSE_PROMPT

logger = logging.getLogger(__name__)


async def composer_node(state: PlatformState) -> PlatformState:
    """组装节点：将研报 + 要闻 + 行业动态组装为每日简报"""
    state["current_step"] = "compose"
    state["progress"] = 82.0

    reports = state.get("research_reports", [])
    clusters = state.get("clusters", [])

    # 构建 TopNews
    top_news = _build_top_news(state)

    # 构建 BriefReports
    brief_reports = _build_brief_reports(reports)

    # 构建 IndustryNews
    industry_news = _build_industry_news(clusters)

    # 构建 SentimentData
    sentiment = _build_sentiment_data()

    # 构建明日关注
    tomorrow = [
        "关注关键经济数据发布",
        "关注行业政策动态",
        "关注国际市场变化",
    ]

    # LLM 生成导语
    try:
        top_news_text = "\n".join(f"{i+1}. {n['title']}" for i, n in enumerate(top_news))
        reports_text = "\n".join(f"- {r['title']}: {r.get('summary', '')}" for r in brief_reports)
        industry_text = "\n".join(
            f"{g['industry']}: {', '.join(g['items'])}" for g in industry_news
        )
        prompt = BRIEF_COMPOSE_PROMPT.format(
            top_news=top_news_text,
            reports=reports_text,
            industry_news=industry_text,
        )
        overview = await call_llm_async(prompt)
    except Exception:
        overview = "今日要闻聚焦关键领域动态，市场情绪总体平稳。"

    brief = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "topNews": top_news,
        "reports": brief_reports,
        "industryNews": industry_news,
        "sentimentData": sentiment,
        "tomorrowFocus": tomorrow,
        "overview": overview,
    }

    state["daily_brief"] = brief
    state["progress"] = 90.0

    # 持久化简报
    try:
        from app.repositories.brief_repo import BriefRepo
        BriefRepo.upsert(brief["date"], brief)
        logger.info(f"[ComposeAgent] 持久化简报到 DB: {brief['date']}")
    except Exception as e:
        logger.warning(f"[ComposeAgent] DB 持久化失败: {e}")

    logger.info("[ComposeAgent] 日报组装完成")
    return state


def _build_top_news(state: PlatformState) -> list[dict]:
    """构建 TopNews 列表"""
    clusters = state.get("clusters", [])
    sorted_clusters = sorted(clusters, key=lambda c: c.get("importance", 0), reverse=True)
    top = []

    for i, cluster in enumerate(sorted_clusters[:5]):
        articles = cluster.get("articles", [])
        rep = cluster.get("representative", articles[0] if articles else {})

        # 构建多源报道聚合列表（取前5篇）
        sources = []
        for a in articles[:5]:
            title = a.get("title", "")
            excerpt_text = a.get("content", "") or a.get("summary", "")
            sources.append({
                "name": a.get("author", a.get("source", "综合媒体")),
                "time": str(a.get("published_at", ""))[:16] if a.get("published_at") else "",
                "title": title,
                "excerpt": excerpt_text[:80] if excerpt_text else title[:80],
                "url": a.get("url", ""),
            })

        top.append({
            "id": f"tn-{i+1}",
            "rank": i + 1,
            "title": rep.get("title", cluster.get("topic_label", "")),
            "summary": cluster.get("summary", ""),
            "source": rep.get("author", rep.get("source", "")),
            "publishedAt": rep.get("published_at", datetime.utcnow().isoformat()),
            "hotIndex": 100 - i * 5,
            "tags": cluster.get("tags", []),
            "sources": sources,
        })

    return top


def _build_brief_reports(reports: list[dict]) -> list[dict]:
    """构建 BriefReport 列表"""
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "summary": r.get("summary", "")[:100],
            "sourceCount": r.get("source_count", 0),
            "generatedAt": r.get("generated_at", "刚刚"),
            "importance": r.get("importance", 3),
            "sections": ["事件背景", "现状分析", "趋势研判", "风险提示"],
        }
        for r in reports[:3]
    ]


def _build_industry_news(clusters: list[dict]) -> list[dict]:
    """构建行业动态分组"""
    industry_map = {}
    for cluster in clusters:
        articles = cluster.get("articles", [])
        if not articles:
            continue
        label = cluster.get("topic_label", "综合")
        item = articles[0]["title"][:30]
        if label not in industry_map:
            industry_map[label] = []
        industry_map[label].append(item)

    icons = ["🏦", "💻", "🏭", "🚗", "📊", "🔬"]
    return [
        {"industry": k, "icon": icons[i % len(icons)], "items": v[:3]}
        for i, (k, v) in enumerate(industry_map.items())
    ]


def _build_sentiment_data() -> dict:
    """构建市场情绪数据"""
    return {
        "sentiment": 72,
        "sentimentLabel": "偏乐观",
        "sentimentTrend": "up",
        "hotIndex": 85,
        "hotLabel": "高",
        "hotTrend": "up",
        "volatility": 45,
        "volatilityLabel": "低",
        "volatilityTrend": "down",
    }
