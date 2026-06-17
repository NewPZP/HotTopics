# 智览平台 — 导入所有模型，确保 Base.metadata.create_all() 能发现所有表
from app.models.database import Base, get_db, init_db
from app.models.article import RawArticle, ProcessedArticle
from app.models.cluster import ClusterModel, ClusterArticleModel
from app.models.report import ReportModel
from app.models.brief import BriefModel
from app.models.topic import TopicModel, DataSourceModel, SystemConfigModel, CrawlerSiteModel
from app.models.workflow import WorkflowRunModel
