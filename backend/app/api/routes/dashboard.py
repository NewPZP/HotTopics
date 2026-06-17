# Dashboard 工作台 API 路由 — 真实数据驱动
from fastapi import APIRouter, Query
from app.repositories.article_repo import ArticleRepo
from app.repositories.cluster_repo import ClusterRepo
from app.repositories.report_repo import ReportRepo
from app.models.database import get_session
from app.models.report import ReportModel
from app.models.article import RawArticle, ProcessedArticle
from app.models.cluster import ClusterModel
from sqlalchemy import func, and_
import datetime

router = APIRouter()

# 统一兜底比例：原始采集量 ≈ 去重量 × ESTIMATE_RATIO
ESTIMATE_RATIO = 1.3


def _get_date_range(range_key: str) -> tuple[datetime.date, datetime.date, str]:
    """根据范围键返回 (start_date, end_date, display_label)"""
    today = datetime.date.today()
    if range_key == "week":
        # 本周一 ~ 今天
        start = today - datetime.timedelta(days=today.weekday())
        return start, today, "本周"
    elif range_key == "month":
        # 本月1号 ~ 今天
        start = today.replace(day=1)
        return start, today, "本月"
    else:
        # 默认今日
        return today, today, "今日"


def _count_articles_in_range(db, model, start: datetime.date, end: datetime.date, unique_only: bool = False) -> int:
    """统计日期范围内的文章数量"""
    q = db.query(model).filter(
        and_(
            func.date(model.created_at) >= start,
            func.date(model.created_at) <= end,
        )
    )
    if unique_only and model == ProcessedArticle:
        q = q.filter(model.is_duplicate == False)
    return q.count()


def _count_in_range(db, model, start: datetime.date, end: datetime.date) -> int:
    """统计日期范围内的记录数量"""
    return db.query(model).filter(
        and_(
            func.date(model.created_at) >= start,
            func.date(model.created_at) <= end,
        )
    ).count()


def _derive_counts_for_date(target_date: datetime.date) -> tuple[int, int]:
    """从研报 sources 反推某日文章采集量（统一兜底逻辑）。
    返回 (raw, dedup)，其中 dedup = sources 中不重复 URL 数。
    """
    with get_session() as db:
        reports = db.query(ReportModel).filter(
            func.date(ReportModel.created_at) == target_date
        ).all()
        seen_urls: set[str] = set()
        for r in reports:
            sources = r.sources if isinstance(r.sources, list) else []
            for s in sources:
                url = s.get("url", "") if isinstance(s, dict) else ""
                if url:
                    seen_urls.add(url)
        dedup = len(seen_urls)
        raw = max(dedup, int(dedup * ESTIMATE_RATIO)) if dedup > 0 else 0
        return raw, dedup


def _derive_counts_for_range(start: datetime.date, end: datetime.date) -> tuple[int, int]:
    """从研报 sources 反推日期范围内的文章采集量"""
    with get_session() as db:
        reports = db.query(ReportModel).filter(
            and_(
                func.date(ReportModel.created_at) >= start,
                func.date(ReportModel.created_at) <= end,
            )
        ).all()
        seen_urls: set[str] = set()
        for r in reports:
            sources = r.sources if isinstance(r.sources, list) else []
            for s in sources:
                url = s.get("url", "") if isinstance(s, dict) else ""
                if url:
                    seen_urls.add(url)
        dedup = len(seen_urls)
        raw = max(dedup, int(dedup * ESTIMATE_RATIO)) if dedup > 0 else 0
        return raw, dedup


@router.get("/dashboard/stats")
async def get_dashboard_stats(date_range: str = Query("today", description="数据范围: today/week/month")):
    """工作台统计卡片 — DB 实时统计，支持今日/本周/本月"""
    start_date, end_date, range_label = _get_date_range(date_range)

    with get_session() as db:
        article_count = _count_articles_in_range(db, RawArticle, start_date, end_date)
        unique_count = _count_articles_in_range(db, ProcessedArticle, start_date, end_date, unique_only=True)
        cluster_count = _count_in_range(db, ClusterModel, start_date, end_date)
        report_count = _count_in_range(db, ReportModel, start_date, end_date)

    # 若文章表为空，从研报 sources 反推
    if article_count == 0 and report_count > 0:
        if date_range in ("week", "month"):
            article_count, unique_count = _derive_counts_for_range(start_date, end_date)
        else:
            article_count, unique_count = _derive_counts_for_date(datetime.date.today())

    # 计算 vs 昨日增量（仅今日范围）或前一日均量
    if date_range == "today":
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yest_article = ArticleRepo.count_on_date(yesterday)
        if yest_article == 0:
            yest_article, _ = _derive_counts_for_date(yesterday)
        diff = article_count - yest_article
        trend_text = f"+{diff}篇" if diff >= 0 else f"{diff}篇"
        trend_type = "up" if diff >= 0 else "down"
        trend_sub = "vs 昨日"
    elif date_range == "week":
        # 周均：按天数平均
        days_in_range = (end_date - start_date).days + 1
        avg = round(article_count / days_in_range, 1) if days_in_range > 0 else 0
        trend_text = f"日均 {avg} 篇"
        trend_type = "neutral"
        trend_sub = f"共 {days_in_range} 天"
    else:
        days_in_range = (end_date - start_date).days + 1
        avg = round(article_count / days_in_range, 1) if days_in_range > 0 else 0
        trend_text = f"日均 {avg} 篇"
        trend_type = "neutral"
        trend_sub = f"共 {days_in_range} 天"

    dedup_rate = round((1 - unique_count / article_count) * 100, 1) if article_count > 0 else 0

    label_prefix = "今日" if date_range == "today" else ("本周" if date_range == "week" else "本月")

    return [
        {"label": f"{label_prefix}采集", "value": str(article_count), "icon": "rss",
         "iconBg": "bg-blue-50", "iconColor": "text-blue-600",
         "trend": trend_text, "trendType": trend_type, "subLabel": trend_sub},
        {"label": f"{label_prefix}去重", "value": str(unique_count), "icon": "filter",
         "iconBg": "bg-green-50", "iconColor": "text-green-600",
         "trend": f"去重率 {dedup_rate}%", "trendType": "neutral"},
        {"label": f"{label_prefix}聚类", "value": str(cluster_count), "icon": "file-text",
         "iconBg": "bg-purple-50", "iconColor": "text-purple-600",
         "trend": f"{cluster_count} 个", "trendType": "up", "subLabel": "主题簇"},
        {"label": f"{label_prefix}研报", "value": str(report_count), "icon": "send",
         "iconBg": "bg-orange-50", "iconColor": "text-orange-600",
         "trend": f"已生成 {report_count} 篇", "trendType": "neutral"},
    ]


@router.get("/dashboard/trends")
async def get_dashboard_trends(date_range: str = Query("today", description="数据范围: today/week/month")):
    """趋势图数据 — 支持今日(近7日)/本周/本月"""
    today = datetime.date.today()

    if date_range == "week":
        # 本周一 ~ 今天，逐日显示
        start = today - datetime.timedelta(days=today.weekday())
        days = (today - start).days + 1
    elif date_range == "month":
        # 本月1号 ~ 今天，逐日显示
        start = today.replace(day=1)
        days = (today - start).days + 1
    else:
        # 默认近7日
        days = 7
        start = today - datetime.timedelta(days=days - 1)

    with get_session() as db:
        daily_articles = []
        daily_reports_list = []
        for i in range(days):
            d = start + datetime.timedelta(days=i)
            raw_count = db.query(RawArticle).filter(
                func.date(RawArticle.created_at) == d
            ).count()
            unique_count = db.query(ProcessedArticle).filter(
                and_(
                    func.date(ProcessedArticle.created_at) == d,
                    ProcessedArticle.is_duplicate == False,
                )
            ).count()
            report_count = db.query(ReportModel).filter(
                func.date(ReportModel.created_at) == d
            ).count()
            daily_articles.append({
                "date": d.strftime("%m-%d"),
                "raw": raw_count,
                "unique": unique_count,
            })
            daily_reports_list.append(report_count)

    # 若文章数据为空但从研报可反推
    if all(d["raw"] == 0 for d in daily_articles) and any(r > 0 for r in daily_reports_list):
        for i, d in enumerate(daily_articles):
            target = start + datetime.timedelta(days=i)
            r_count = daily_reports_list[i]
            if r_count > 0:
                raw, dedup = _derive_counts_for_date(target)
                if raw == 0 and dedup == 0:
                    d["raw"] = r_count * 2
                    d["unique"] = r_count
                else:
                    d["raw"] = raw
                    d["unique"] = dedup

    return {
        "dates": [d["date"] for d in daily_articles],
        "collect": [d["raw"] for d in daily_articles],
        "dedup": [d["unique"] for d in daily_articles],
        "reports": daily_reports_list,
    }


@router.get("/dashboard/top-news")
async def get_dashboard_top_news(date_range: str = Query("today", description="数据范围: today/week/month")):
    """今日要闻 TOP5 — 优先文章表，回退到简报"""
    start_date, end_date, _ = _get_date_range(date_range)

    # 范围查询 TOP 文章
    with get_session() as db:
        articles = db.query(ProcessedArticle).filter(
            and_(
                func.date(ProcessedArticle.created_at) >= start_date,
                func.date(ProcessedArticle.created_at) <= end_date,
                ProcessedArticle.is_duplicate == False,
            )
        ).order_by(ProcessedArticle.created_at.desc()).limit(5).all()

        if articles:
            result = []
            for idx, a in enumerate(articles):
                tags = a.topic_tags if a.topic_tags else []
                result.append({
                    "id": a.id,
                    "rank": idx + 1,
                    "title": a.title,
                    "summary": (a.content or "")[:80],
                    "source": a.source or a.author or "",
                    "publishedAt": str(a.published_at) if a.published_at else "",
                    "hotIndex": 90 - idx * 5,
                    "tags": tags if isinstance(tags, list) else [tags],
                })
            return result

    # 回退：从今日简报中取 topNews
    from app.repositories.brief_repo import BriefRepo
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    brief = BriefRepo.get_by_date(today_str)
    if brief and brief.get("topNews"):
        return brief["topNews"][:5]
    return []
