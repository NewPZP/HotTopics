import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.models.database import get_session
from app.models.workflow import WorkflowRunModel

with get_session() as db:
    stuck = db.query(WorkflowRunModel).filter(
        WorkflowRunModel.status == 'running'
    ).all()
    
    for w in stuck:
        print(f'Fixing stuck: {w.id}')
        w.status = 'failed'
        w.error_message = 'Process terminated - previous session'
    
    db.commit()
    print(f'Fixed {len(stuck)} stuck records')
