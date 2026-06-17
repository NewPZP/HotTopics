import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.models.database import get_session
from app.models.report import ReportModel
from app.models.cluster import ClusterModel
from app.models.article import RawArticle, ProcessedArticle

with get_session() as db:
    print("=" * 60)
    print("=== Reports (研报) ===")
    for r in db.query(ReportModel).all():
        print(f"  [{r.id}] {r.title}")
        summary = (r.summary or "N/A")[:120]
        print(f"    summary: {summary}...")
        print(f"    status: {r.status}, importance: {r.importance}, cluster: {r.cluster_id}")
        print(f"    sections: {(r.sections or 'N/A')[:80]}...")
        print()

    print("=" * 60)
    print("=== Clusters (聚类) ===")
    for c in db.query(ClusterModel).all():
        print(f"  [{c.id}] {c.topic_label}")
        print(f"    article_count: {c.article_count}, importance: {c.importance}")
        summary = (c.summary or "N/A")[:120]
        print(f"    summary: {summary}...")
        print(f"    tags: {c.tags}")
        print()

    print("=" * 60)
    print(f"RawArticle: {db.query(RawArticle).count()}")
    print(f"ProcessedArticle: {db.query(ProcessedArticle).count()}")
