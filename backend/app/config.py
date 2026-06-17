# 智览平台 — 后端配置管理
import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # ── 应用基础 ──
    APP_NAME: str = "智览平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # ── 数据库 (MySQL 必需) ──
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "wisdom123"
    DB_NAME: str = "wisdom_view"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # ── Redis (必需) ──
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ── Elasticsearch (必需) ──
    ES_HOST: str = "http://localhost:9200"
    ES_USER: Optional[str] = None
    ES_PASSWORD: Optional[str] = None
    ES_INDEX_PREFIX: str = "wisdom_view"

    # ── LLM (DashScope / 通义千问) ──
    DASHSCOPE_API_KEY: str = ""
    LLM_MODEL: str = "qwen-max"
    EMBEDDING_MODEL: str = "text-embedding-v3"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4096

    # ── 任务调度 ──
    COLLECT_CRON: str = "0 */2 * * *"       # 默认每2小时采集
    BRIEF_GEN_TIME: str = "18:00"           # 默认每日18:00生成日报

    # ── 文件存储 ──
    EXPORT_DIR: str = "./exports"
    TEMPLATE_DIR: str = "./templates"

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ── WebSocket ──
    WS_PING_INTERVAL: int = 30
    WS_PING_TIMEOUT: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
