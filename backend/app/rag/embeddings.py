# Embedding 服务 — 基于 DashScope text-embedding-v3
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_embedding(text: str) -> Optional[list[float]]:
    """获取文本向量"""
    if not settings.DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY 未配置，返回伪向量")
        return _mock_embedding(text)

    try:
        from dashscope import TextEmbedding
        resp = TextEmbedding.call(
            api_key=settings.DASHSCOPE_API_KEY,
            model=settings.EMBEDDING_MODEL,
            input=text[:2048],
        )
        if resp.status_code == 200:
            return resp.output.embeddings[0].embedding
        else:
            logger.error(f"Embedding调用失败: {resp.code} - {resp.message}")
            return _mock_embedding(text)
    except Exception as e:
        logger.error(f"Embedding调用异常: {e}")
        return _mock_embedding(text)


def _mock_embedding(text: str) -> list[float]:
    """生成模拟向量（开发调试用）"""
    import hashlib
    import struct
    h = hashlib.sha256(text.encode()).digest()
    dim = 128
    return [struct.unpack('f', h[i*4:(i+1)*4])[0] / 1e10 for i in range(min(dim, len(h)//4))]
