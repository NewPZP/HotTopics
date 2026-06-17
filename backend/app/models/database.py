# 数据库连接与基础模型 (MySQL)
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session() -> Session:
    """获取数据库会话（供 Agent / 非 FastAPI 上下文使用）
    
    用法:
        with get_session() as db:
            db.query(...).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_db_initialized = False


def init_db():
    """创建所有表（仅在首次启动时执行）"""
    global _db_initialized
    if _db_initialized:
        return
    Base.metadata.create_all(bind=engine)
    _db_initialized = True
