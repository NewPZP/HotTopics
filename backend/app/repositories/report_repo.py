# Report Repository — 研报 CRUD
import re
from sqlalchemy import func
from app.models.database import get_session
from app.models.report import ReportModel


def _clean_tags(tags: list, title: str = "") -> list:
    """清理乱码标签，过滤掉含过多乱码字符的标签"""
    if not tags:
        return []
    cleaned = []
    for tag in tags:
        if not isinstance(tag, str):
            continue
        valid = len(re.findall(r'[\u4e00-\u9fff\w]', tag))
        total = max(len(tag), 1)
        ratio = valid / total
        if ratio < 0.5 or tag.count('?') > len(tag) * 0.4:
            continue
        tag = re.sub(r'[^\u4e00-\u9fff\w\s]', '', tag).strip()
        if tag:
            cleaned.append(tag)
    return cleaned


class ReportRepo:

    @staticmethod
    def list_all(search: str = "", topic: str = "", sort: str = "time") -> list[dict]:
        """列出所有研报，支持搜索/主题过滤/排序"""
        with get_session() as db:
            q = db.query(ReportModel)
            if search:
                q = q.filter(
                    (ReportModel.title.contains(search)) |
                    (ReportModel.summary.contains(search))
                )
            if topic:
                # JSON 数组字段中包含指定主题标签
                q = q.filter(ReportModel.tags.contains(topic))
            if sort == "importance":
                q = q.order_by(ReportModel.importance.desc())
            else:
                q = q.order_by(ReportModel.created_at.desc())
            return [_report_to_dict(r) for r in q.all()]

    @staticmethod
    def get_by_id(report_id: str) -> dict | None:
        """按 ID 获取研报"""
        with get_session() as db:
            r = db.query(ReportModel).filter(ReportModel.id == report_id).first()
            return _report_to_dict(r) if r else None

    @staticmethod
    def count_today() -> int:
        """今日研报数量"""
        import datetime
        with get_session() as db:
            today = datetime.date.today()
            return db.query(ReportModel).filter(
                func.date(ReportModel.created_at) == today
            ).count()

    @staticmethod
    def get_daily_counts(days: int = 7) -> list[int]:
        """近 N 天每日研报数量"""
        import datetime
        with get_session() as db:
            results = []
            for i in range(days - 1, -1, -1):
                d = datetime.date.today() - datetime.timedelta(days=i)
                c = db.query(ReportModel).filter(
                    func.date(ReportModel.created_at) == d
                ).count()
                results.append(c)
            return results

    @staticmethod
    def upsert(report: dict) -> dict:
        """创建或更新研报"""
        with get_session() as db:
            r = db.query(ReportModel).filter(ReportModel.id == report["id"]).first()
            if r:
                for k, v in report.items():
                    if hasattr(r, k) and k != "id":
                        setattr(r, k, v)
            else:
                r = ReportModel(
                    id=report["id"],
                    title=report.get("title", ""),
                    subtitle=report.get("subtitle", ""),
                    summary=report.get("summary", ""),
                    generated_at=report.get("generatedAt", ""),
                    source_count=report.get("sourceCount", 0),
                    importance=report.get("importance", 3),
                    time_span=report.get("timeSpan", ""),
                    tags=report.get("tags", []),
                    is_featured=report.get("isFeatured", False),
                    status=report.get("status", "published"),
                    cluster_id=report.get("clusterId", ""),
                    sections=report.get("sections", []),
                    sources=report.get("sources", []),
                )
                db.add(r)
            db.commit()
            return _report_to_dict(r)


def _report_to_dict(r: ReportModel) -> dict:
    # 补全缺失字段
    generated_at = r.generated_at if r.generated_at else (r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "刚刚")
    
    sources = r.sources if isinstance(r.sources, list) else []
    source_count = r.source_count if (r.source_count and r.source_count > 0) else len(sources)

    return {
        "id": r.id,
        "title": r.title,
        "subtitle": r.subtitle or "",
        "summary": r.summary or "",
        "generatedAt": generated_at,
        "sourceCount": source_count,
        "importance": r.importance or 3,
        "timeSpan": r.time_span or "",
        "tags": _clean_tags(r.tags or [], r.title or ""),
        "isFeatured": r.is_featured or False,
        "status": r.status or "published",
        "sections": r.sections or [],
        "sources": sources,
    }
