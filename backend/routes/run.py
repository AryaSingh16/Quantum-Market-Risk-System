from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.runner import run_engine_pipeline, EngineExecutionError

router = APIRouter()

def execute_pipeline_task(mode: str):
    try:
        run_engine_pipeline(mode)
    except Exception as e:
        print(f"Background execution failed: {e}")

@router.post("/run")
def run_risk_engine(background_tasks: BackgroundTasks, mode: str = "FULL"):
    """
    Triggers the risk engine pipeline to run asynchronously in the background.
    """
    background_tasks.add_task(execute_pipeline_task, mode)
    return {
        "status": "ACCEPTED",
        "message": f"Risk engine started in {mode} mode. Check results/summary when complete.",
    }
