# LangGraph 工作流状态定义
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PlatformState(TypedDict, total=False):
    # ── 输入参数 ──
    topics: list[str]               # 监控主题列表
    date_range: tuple[str, str]     # 时间范围
    run_id: str                     # 本次运行ID
    max_retries: int                # 最大重试次数，默认3

    # ── 消息传递 ──
    messages: Annotated[list[BaseMessage], add_messages]

    # ── 采集阶段 ──
    raw_articles: list[dict]        # 原始文章 [{id, source, title, content, url, ...}]
    collection_errors: list[str]    # 采集错误信息
    collect_count: int              # 采集总数量

    # ── 预处理阶段 ──
    cleaned_articles: list[dict]    # 清洗后文章
    preprocess_errors: list[str]

    # ── 去重阶段 ──
    duplicates_removed: int         # 去重数量
    unique_articles: list[dict]     # 去重后文章
    dedup_details: dict             # 去重详情

    # ── 聚类阶段 ──
    clusters: list[dict]            # 聚类结果 [{cluster_id, topic_label, articles, ...}]
    cluster_labels: list[str]       # 聚类标签
    cluster_count: int              # 聚类数量

    # ── RAG检索与摘要阶段 ──
    research_reports: list[dict]    # 深度研报
    rag_context: list[dict]         # RAG检索上下文
    research_count: int             # 研报数量

    # ── 审核阶段 ──
    review_passed: bool             # 审核是否通过
    review_feedback: list[str]      # 审核反馈
    retry_count: int                # 当前重试次数

    # ── 组装阶段 ──
    daily_brief: dict               # 日报数据

    # ── 导出阶段 ──
    markdown_content: str           # Markdown内容
    pdf_path: str                   # PDF文件路径

    # ── 推送阶段 ──
    dispatch_status: dict           # 推送状态 {channel: success/failed}

    # ── 元信息 ──
    current_step: str               # 当前步骤名
    progress: float                 # 进度 0.0~100.0
    errors: list[str]               # 全局错误列表
