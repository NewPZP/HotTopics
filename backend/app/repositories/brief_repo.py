# Brief Repository — 简报 CRUD
from app.models.database import get_session
from app.models.brief import BriefModel
from app.repositories.report_repo import _clean_tags


class BriefRepo:

    @staticmethod
    def list_all() -> list[dict]:
        """列出所有简报"""
        with get_session() as db:
            briefs = db.query(BriefModel).order_by(BriefModel.date.desc()).all()
            return [_brief_to_dict(b) for b in briefs]

    @staticmethod
    def get_by_date(date: str) -> dict | None:
        """按日期获取简报"""
        with get_session() as db:
            b = db.query(BriefModel).filter(BriefModel.date == date).first()
            return _brief_to_dict(b) if b else None

    @staticmethod
    def upsert(date: str, data: dict) -> dict:
        """创建或更新简报"""
        with get_session() as db:
            b = db.query(BriefModel).filter(BriefModel.date == date).first()
            if b:
                b.top_news = data.get("topNews")
                b.reports = data.get("reports")
                b.industry_news = data.get("industryNews")
                b.sentiment_data = data.get("sentimentData")
                b.tomorrow_focus = data.get("tomorrowFocus")
                b.markdown_content = data.get("markdownContent")
                b.pdf_path = data.get("pdfPath")
            else:
                import uuid
                b = BriefModel(
                    id=f"brief-{uuid.uuid4().hex[:8]}",
                    date=date,
                    top_news=data.get("topNews"),
                    reports=data.get("reports"),
                    industry_news=data.get("industryNews"),
                    sentiment_data=data.get("sentimentData"),
                    tomorrow_focus=data.get("tomorrowFocus"),
                    markdown_content=data.get("markdownContent"),
                    pdf_path=data.get("pdfPath"),
                    status="published",
                )
                db.add(b)
            db.commit()
            return _brief_to_dict(b)


def _brief_to_dict(b: BriefModel) -> dict:
    top_news = []
    for item in (b.top_news or []):
        item = dict(item)
        item["tags"] = _clean_tags(item.get("tags", []), item.get("title", ""))
        # 修复 source 字段：若为列表则取第一个元素或源标题
        src = item.get("source", "")
        if isinstance(src, list):
            cleaned = _clean_tags(src)
            item["source"] = ", ".join(cleaned[:3]) if cleaned else "综合媒体"
        elif not src or src.count('?') > len(src) * 0.3:
            item["source"] = "综合媒体"
        top_news.append(item)
    return {
        "date": b.date,
        "topNews": top_news,
        "reports": b.reports or [],
        "industryNews": b.industry_news or [],
        "sentimentData": b.sentiment_data or {},
        "tomorrowFocus": b.tomorrow_focus or [],
    }
