# LLM 调用封装 — 基于 DashScope (通义千问)
import json
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Optional
from dashscope import Generation
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# LLM 调用线程池 + 超时控制
_llm_executor = ThreadPoolExecutor(max_workers=10)
LLM_TIMEOUT = 120  # 单次 LLM 调用超时秒数


def call_llm(prompt: str, system_prompt: str = "", temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
    """调用通义千问 LLM（同步版本，含 HTTP 超时保护）"""

    if not settings.DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY 未配置，返回模拟响应")
        return _mock_response(prompt)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # 用独立线程执行 HTTP 调用，future.result(timeout) 控制超时
    # 注意：不用 with 管理 executor，避免 shutdown(wait=True) 等待卡住的线程
    inner_executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = inner_executor.submit(
            _do_llm_call,
            api_key=settings.DASHSCOPE_API_KEY,
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=temperature or settings.LLM_TEMPERATURE,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )
        return future.result(timeout=LLM_TIMEOUT)
    except FutureTimeout:
        logger.error(f"LLM HTTP调用超时 ({LLM_TIMEOUT}s)，使用模拟响应")
        future.cancel()
        inner_executor.shutdown(wait=False)  # 不等待卡住的线程
        return _mock_response(prompt)
    except Exception as e:
        logger.error(f"LLM调用异常: {e}")
        inner_executor.shutdown(wait=False)
        return _mock_response(prompt)


def _do_llm_call(api_key: str, model: str, messages: list, temperature: float, max_tokens: int) -> str:
    """实际执行 DashScope API 调用（在独立线程中运行）"""
    response = Generation.call(
        api_key=api_key,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        result_format="message",
    )
    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        raise RuntimeError(f"{response.code}: {response.message}")


async def call_llm_async(prompt: str, system_prompt: str = "", temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
    """调用通义千问 LLM（异步版本，不阻塞事件循环；超时由 call_llm 内部保证）"""
    if not settings.DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY 未配置，返回模拟响应")
        return _mock_response(prompt)

    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(
            _llm_executor,
            call_llm,
            prompt,
            system_prompt,
            temperature,
            max_tokens,
        )
    except Exception as e:
        logger.error(f"LLM异步调用异常: {e}")
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """当 API Key 未配置时，返回模拟响应（用于开发调试）"""
    if "摘要" in prompt or "提炼" in prompt:
        return "本文报道了相关领域的最新动态，涉及政策调整、市场变化和行业趋势等多个方面，值得持续关注。"

    if "标签" in prompt and "文章" in prompt:
        return "综合资讯"

    if "审核" in prompt:
        return json.dumps({"passed": True, "score": 85, "issues": [], "suggestions": ["内容完整，格式规范"]}, ensure_ascii=False)

    if "查询" in prompt and "扩展" in prompt:
        # Query rewrite mock
        return "\n".join(["政策监管 法规", "市场影响 行业分析", "国际动态 比较"])

    if "导语" in prompt or "概览" in prompt:
        return "今日要闻聚焦于宏观经济政策调整、科技创新突破及国际市场动态。央行释放流动性信号，AI芯片管制引发产业链关注，新能源车市持续活跃。整体市场情绪偏乐观，建议关注明日关键数据发布。"

    return "分析完成。"
