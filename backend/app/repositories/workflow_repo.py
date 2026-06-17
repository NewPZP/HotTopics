# Workflow Repository — 工作流运行记录 CRUD
from app.models.database import get_session
from app.models.workflow import WorkflowRunModel


class WorkflowRepo:

    @staticmethod
    def start_run(run_id: str, topics: list[str], checkpoints: dict = None) -> dict:
        """记录工作流开始"""
        with get_session() as db:
            run = WorkflowRunModel(
                id=run_id,
                status="running",
                step="init",
                progress=0.0,
                input_state={"topics": topics},
                checkpoints=checkpoints or {},
            )
            db.add(run)
            db.commit()
            return _run_to_dict(run)

    @staticmethod
    def update_progress(run_id: str, step: str, progress: float, output_state: dict = None):
        """更新工作流进度"""
        with get_session() as db:
            run = db.query(WorkflowRunModel).filter(WorkflowRunModel.id == run_id).first()
            if run:
                run.step = step
                run.progress = progress
                if output_state:
                    run.output_state = output_state
                db.commit()

    @staticmethod
    def complete_run(run_id: str, output_state: dict = None):
        """标记工作流完成"""
        import datetime
        with get_session() as db:
            run = db.query(WorkflowRunModel).filter(WorkflowRunModel.id == run_id).first()
            if run:
                run.status = "completed"
                run.progress = 100.0
                run.completed_at = datetime.datetime.utcnow()
                if output_state:
                    run.output_state = output_state
                db.commit()

    @staticmethod
    def fail_run(run_id: str, error_message: str):
        """标记工作流失败"""
        with get_session() as db:
            run = db.query(WorkflowRunModel).filter(WorkflowRunModel.id == run_id).first()
            if run:
                run.status = "failed"
                run.error_message = error_message
                db.commit()

    @staticmethod
    def get_latest() -> dict | None:
        """获取最近一次工作流运行"""
        with get_session() as db:
            run = db.query(WorkflowRunModel).order_by(
                WorkflowRunModel.created_at.desc()
            ).first()
            return _run_to_dict(run) if run else None

    @staticmethod
    def has_any_data() -> bool:
        """是否有任何历史采集数据（文章/聚类/研报）"""
        from app.models.article import RawArticle
        with get_session() as db:
            return db.query(RawArticle).count() > 0

    @staticmethod
    def is_running() -> bool:
        """是否有正在运行的工作流"""
        with get_session() as db:
            return db.query(WorkflowRunModel).filter(
                WorkflowRunModel.status == "running"
            ).count() > 0

    @staticmethod
    def get_all_running() -> list[dict]:
        """获取所有运行中的工作流"""
        with get_session() as db:
            runs = db.query(WorkflowRunModel).filter(
                WorkflowRunModel.status == "running"
            ).all()
            return [_run_to_dict(r) for r in runs]

    @staticmethod
    def fail_all_running(error_message: str):
        """批量标记所有运行中工作流为失败"""
        import datetime
        with get_session() as db:
            db.query(WorkflowRunModel).filter(
                WorkflowRunModel.status == "running"
            ).update({
                "status": "failed",
                "error_message": error_message,
                "completed_at": datetime.datetime.utcnow(),
            })
            db.commit()


def _run_to_dict(run: WorkflowRunModel) -> dict:
    return {
        "runId": run.id,
        "status": run.status,
        "step": run.step,
        "progress": run.progress or 0,
        "startedAt": str(run.started_at) if run.started_at else "",
        "completedAt": str(run.completed_at) if run.completed_at else "",
    }
