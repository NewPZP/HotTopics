# DispatchAgent — 推送分发
import logging
from app.agents.state import PlatformState

logger = logging.getLogger(__name__)


async def dispatcher_node(state: PlatformState) -> PlatformState:
    """推送节点：完成工作流，记录结果"""
    state["current_step"] = "dispatch"
    state["progress"] = 98.0

    brief = state.get("daily_brief", {})
    markdown = state.get("markdown_content", "")
    pdf_path = state.get("pdf_path", "")

    dispatch_status = {
        "api": "success",
        "file_download": "success" if markdown else "skipped",
        "pdf_path": pdf_path,
        "brief_date": brief.get("date", ""),
    }

    state["dispatch_status"] = dispatch_status
    state["progress"] = 100.0

    logger.info(f"[DispatchAgent] 推送完成: {dispatch_status}")
    return state
