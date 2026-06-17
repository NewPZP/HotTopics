"""检查数据库真实数据状态"""
import sys
sys.path.insert(0, '.')

from app.models.database import get_session
from app.models.workflow import WorkflowRunModel
from app.models.article import RawArticle, ProcessedArticle
from app.models.cluster import ClusterModel, ClusterArticleModel
from app.models.report import ReportModel
from app.models.brief import BriefModel

with get_session() as db:
    print("=== 数据库真实数据状态 ===")
    print(f"Workflow 运行记录: {db.query(WorkflowRunModel).count()}")
    print(f"原始文章 (Raw): {db.query(RawArticle).count()}")
    print(f"处理后文章 (Processed): {db.query(ProcessedArticle).count()}")
    print(f"聚类 (Clusters): {db.query(ClusterModel).count()}")
    print(f"研报 (Reports): {db.query(ReportModel).count()}")
    print(f"简报 (Briefs): {db.query(BriefModel).count()}")
    
    # 显示最新 workflow run
    latest = db.query(WorkflowRunModel).order_by(WorkflowRunModel.created_at.desc()).first()
    if latest:
        print(f"\n最新运行: id={latest.id}, status={latest.status}, step={latest.step}, progress={latest.progress}")
        if latest.error_message:
            print(f"错误: {latest.error_message}")
    
    # 显示 topics
    from app.models.topic import TopicModel
    topics = db.query(TopicModel).all()
    print(f"\n主题 ({len(topics)}):")
    for t in topics:
        print(f"  {t.id}: {t.name} (enabled={t.enabled})")
    
    # 显示 configs
    from app.models.config import SystemConfigModel
    configs = db.query(SystemConfigModel).all()
    print(f"\n系统配置 ({len(configs)}):")
    for c in configs:
        print(f"  {c.key}: {c.value}")
