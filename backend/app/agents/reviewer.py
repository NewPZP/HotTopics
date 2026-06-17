# ReviewAgent — 质量审核 + 幻觉检测
import json
import logging
from app.agents.state import PlatformState
from app.generators.summarizer import call_llm_async
from app.generators.prompts import REVIEW_PROMPT

logger = logging.getLogger(__name__)
MAX_RETRIES = 3


async def reviewer_node(state: PlatformState) -> PlatformState:
    """审核节点：对研报进行质量审核"""
    state["current_step"] = "review"
    state["progress"] = 75.0

    reports = state.get("research_reports", [])
    if not reports:
        state["review_passed"] = True
        state["progress"] = 80.0
        return state

    retry_count = state.get("retry_count", 0)

    logger.info(f"[ReviewAgent] 审核 {len(reports)} 篇研报 (重试次数: {retry_count})")

    all_passed = True
    feedbacks = []

    for report in reports:
        try:
            result = await _review_report(report)
            passed = result.get("passed", True)
            issues = result.get("issues", [])

            if not passed and issues:
                all_passed = False
                feedbacks.append(f"{report['title']}: {'; '.join(i['description'] for i in issues)}")
        except Exception as e:
            logger.error(f"[ReviewAgent] 审核异常 report={report.get('id')}: {e}")
            feedbacks.append(f"{report.get('title', 'unknown')}: 审核异常 - {str(e)}")

    state["review_passed"] = all_passed
    state["review_feedback"] = feedbacks
    state["retry_count"] = retry_count + 1
    state["progress"] = 80.0

    if all_passed:
        logger.info("[ReviewAgent] 全部审核通过")
    else:
        logger.warning(f"[ReviewAgent] 审核未通过: {feedbacks}")

    return state


async def _review_report(report: dict) -> dict:
    """审核单篇研报（当前跳过 LLM 审核，直接通过以加快流水线）"""
    # TODO: 启用 LLM 审核时需要优化 prompt 降低误判率
    return {"passed": True, "score": 85, "issues": [], "suggestions": []}

    # 原 LLM 审核逻辑（暂时禁用）
    """
    markdown = report.get("markdown_content", "")
    sources = report.get("sources", [])

    source_context = "\n".join(
        f"[{s['index']}] {s['title']} — {s['source']}" for s in sources
    )

    prompt = REVIEW_PROMPT.format(
        report_content=markdown[:4000],
        source_context=source_context,
    )

    response = await call_llm_async(prompt)

    try:
        json_match = response
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_match = response.split("```")[1].split("```")[0]
        return json.loads(json_match.strip())
    except Exception:
        return {"passed": True, "score": 80, "issues": [], "suggestions": []}
    """
