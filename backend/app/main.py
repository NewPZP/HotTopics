# 智览平台 — FastAPI 应用入口
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    # 初始化数据库（创建表）
    from app.models.database import init_db
    init_db()

    # 种子数据
    from app.seed import seed_all
    seed_all()

    # 初始化 Redis（可选：失败不阻塞启动）
    try:
        from app.cache.redis_cache import init_redis
        await init_redis()
    except Exception as e:
        logging.warning(f"Redis 初始化失败（跳过）: {e}")

    # 初始化 ES（可选）
    try:
        from elasticsearch import AsyncElasticsearch
        es_kwargs = {"hosts": [settings.ES_HOST]}
        if settings.ES_USER and settings.ES_PASSWORD:
            es_kwargs["basic_auth"] = (settings.ES_USER, settings.ES_PASSWORD)
        es = AsyncElasticsearch(**es_kwargs)
        if await es.ping():
            logging.info("Elasticsearch 连接成功")
        else:
            logging.warning("Elasticsearch ping 失败，请检查 ES 服务及认证配置")
        await es.close()
    except Exception as e:
        logging.warning(f"Elasticsearch 初始化失败（跳过）: {e}")

    # 确保导出目录存在
    import os
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)

    from app.scheduler.jobs import start_scheduler
    start_scheduler()

    # 首次启动自动采集（若无历史数据）
    # 注意：初始采集耗时长（爬虫 + BeautifulSoup），
    # 已从 lifespan 移至 /api/v1/collect/trigger 手动触发，
    # 避免阻塞事件循环导致 API 超时。
    # import asyncio
    # from app.repositories.workflow_repo import WorkflowRepo
    # if not WorkflowRepo.has_any_data():
    #     logging.info("检测到首次启动，触发初始采集...")
    #     asyncio.create_task(_initial_collect())

    yield

    # 关闭时
    from app.scheduler.jobs import shutdown_scheduler
    shutdown_scheduler()

    from app.cache.redis_cache import close_redis
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 注册 REST API 路由 ──
from app.api.routes import (
    briefs, reports, clusters, topics,
    monitor, dashboard, config, collect, crawler_sites,
)

app.include_router(collect.router, prefix="/api/v1", tags=["采集"])
app.include_router(topics.router, prefix="/api/v1", tags=["主题"])
app.include_router(briefs.router, prefix="/api/v1", tags=["简报"])
app.include_router(reports.router, prefix="/api/v1", tags=["研报"])
app.include_router(clusters.router, prefix="/api/v1", tags=["聚类"])
app.include_router(monitor.router, prefix="/api/v1", tags=["监控"])

# 安装内存日志处理器，供监控页面实时展示日志
from app.api.routes.monitor import install_memory_log_handler
install_memory_log_handler()

app.include_router(dashboard.router, prefix="/api/v1", tags=["工作台"])
app.include_router(config.router, prefix="/api/v1", tags=["配置"])
app.include_router(crawler_sites.router, prefix="/api/v1", tags=["爬虫站点"])

# ── 注册 WebSocket ──
from app.api.websocket import ws_router
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


async def _initial_collect():
    """后台异步执行首次采集"""
    import logging
    try:
        from app.agents.graph import run_workflow
        from app.repositories.topic_repo import TopicRepo
        keywords = TopicRepo.get_enabled_keywords()
        await run_workflow(topics=keywords)
        logging.info("初始采集完成")
    except Exception as e:
        logging.error(f"初始采集失败: {e}")
