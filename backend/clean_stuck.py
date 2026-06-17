"""清理旧 stuck 工作流记录"""
import sys
sys.path.insert(0, '.')
from app.models.database import get_session
from app.models.workflow import WorkflowRunModel

with get_session() as db:
    count = db.query(WorkflowRunModel).count()
    print(f"清理前 workflow_runs: {count}")
    db.query(WorkflowRunModel).delete()
    db.commit()
    print("已清理所有 workflow_runs 记录")
