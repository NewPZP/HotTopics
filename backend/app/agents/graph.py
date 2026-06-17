# LangGraph 工作流编排 — 状态图定义
import asyncio
import logging
from langgraph.graph import StateGraph, END
from app.agents.state import PlatformState

logger = logging.getLogger(__name__)

# 导入所有 Agent 节点
from app.agents.collector import collector_node
from app.agents.preprocessor import preprocessor_node
from app.agents.dedup import dedup_node
from app.agents.cluster import cluster_node
from app.agents.researcher import researcher_node
from app.agents.reviewer import reviewer_node
from app.agents.composer import composer_node
from app.agents.exporter import exporter_node
from app.agents.dispatcher import dispatcher_node

# ── 所有节点原始函数（名称 → 函数） ──
_NODE_FNS = {
    "collect": collector_node,
    "preprocess": preprocessor_node,
    "dedup": dedup_node,
    "cluster": cluster_node,
    "research": researcher_node,
    "review": reviewer_node,
    "compose": composer_node,
    "export": exporter_node,
    "dispatch": dispatcher_node,
}

# 已取消的工作流 run_id 集合（用于协作式取消）
_cancelled_runs: set[str] = set()


def cancel_workflow(run_id: str):
    """标记工作流为已取消"""
    _cancelled_runs.add(run_id)
    logger.info(f"工作流已标记取消: {run_id}")


def _make_progress_wrapper(original_fn, step_name: str, run_id: str):
    """为节点函数包裹进度持久化 + WebSocket 广播逻辑"""
    async def wrapped(state: PlatformState) -> PlatformState:
        # 检查是否已被取消
        if run_id in _cancelled_runs:
            logger.warning(f"工作流 {run_id} 已被取消，跳过节点 {step_name}")
            state["current_step"] = step_name
            return state

        result = await original_fn(state)

        current_step = result.get("current_step", step_name)
        current_progress = result.get("progress", 0)

        # 1) 持久化进度到数据库
        try:
            from app.repositories.workflow_repo import WorkflowRepo
            WorkflowRepo.update_progress(run_id, current_step, current_progress)
        except Exception as e:
            logger.warning(f"进度持久化失败 [{step_name}]: {e}")

        # 2) WebSocket 实时广播（fire-and-forget，不阻塞工作流）
        try:
            from app.api.websocket import broadcast_workflow_progress
            asyncio.create_task(broadcast_workflow_progress({
                "type": "workflow:progress",
                "data": {
                    "step": current_step,
                    "progress": current_progress,
                    "run_id": run_id,
                },
            }))
        except Exception as e:
            logger.warning(f"WebSocket广播失败 [{step_name}]: {e}")

        return result
    return wrapped


def _build_workflow(run_id: str) -> StateGraph:
    """构建 LangGraph 工作流（每次运行时动态构建，注入 run_id）"""
    workflow = StateGraph(PlatformState)

    # ── 注册节点（包裹进度持久化 + WebSocket 广播） ──
    for name, fn in _NODE_FNS.items():
        workflow.add_node(name, _make_progress_wrapper(fn, name, run_id))

    # ── 定义边 ──
    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "preprocess")
    workflow.add_edge("preprocess", "dedup")
    workflow.add_edge("dedup", "cluster")
    workflow.add_edge("cluster", "research")
    workflow.add_edge("research", "review")

    # 条件边：审核 → compose 或 research (重试)
    workflow.add_conditional_edges(
        "review",
        _review_router,
        {
            "compose": "compose",
            "research": "research",
        },
    )

    workflow.add_edge("compose", "export")
    workflow.add_edge("export", "dispatch")
    workflow.add_edge("dispatch", END)

    return workflow


def _review_router(state: PlatformState) -> str:
    """审核路由：
    - 通过 → compose
    - 不通过且未超重试次数 → research（重新生成）
    - 不通过且超重试次数 → compose（强制通过）
    """
    max_retries = state.get("max_retries", 3)
    retry_count = state.get("retry_count", 0)

    if state.get("review_passed", False):
        return "compose"

    if retry_count >= max_retries:
        logger.warning(f"审核已达最大重试次数 ({max_retries})，强制通过")
        return "compose"

    logger.info(f"审核未通过，重新生成 (重试 {retry_count}/{max_retries})")
    return "research"


# ── 默认编译（兼容旧代码的模块级引用） ──
_default_workflow = _build_workflow("default")
app_graph = _default_workflow.compile()


async def run_workflow(
    topics: list[str] = None,
    date_range: tuple[str, str] = None,
    run_async: bool = True,
) -> PlatformState:
    """运行完整工作流（每次动态构建图以确保进度被实时追踪）"""
    if topics is None:
        topics = ["AI监管", "金融政策", "新能源"]

    import uuid as _uuid
    run_id = f"run-{_uuid.uuid4().hex[:8]}"

    initial_state: PlatformState = {
        "topics": topics,
        "date_range": date_range or ("", ""),
        "run_id": run_id,
        "max_retries": 3,
        "progress": 0.0,
        "current_step": "init",
        "retry_count": 0,
    }

    # 记录工作流开始
    try:
        from app.repositories.workflow_repo import WorkflowRepo
        WorkflowRepo.start_run(run_id, topics)
    except Exception as e:
        logger.warning(f"无法记录工作流开始: {e}")

    logger.info(f"启动工作流 run_id={run_id}, topics={topics}")

    # 动态构建带回调的图
    run_graph = _build_workflow(run_id).compile()
    final_state = await run_graph.ainvoke(initial_state)

    # 记录工作流结束（检查是否被取消）
    try:
        if run_id in _cancelled_runs:
            WorkflowRepo.fail_run(run_id, "用户手动重置")
            _cancelled_runs.discard(run_id)
            logger.info(f"工作流已取消 run_id={run_id}")
        else:
            WorkflowRepo.complete_run(run_id)
    except Exception as e:
        logger.warning(f"无法记录工作流完成: {e}")

    logger.info(f"工作流完成 run_id={run_id}, 进度: {final_state.get('progress', 0)}%")
    return final_state
