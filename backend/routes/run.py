from fastapi import APIRouter, HTTPException
from backend.runner import run_engine_pipeline, EngineExecutionError

router = APIRouter()


@router.post("/run")
def run_risk_engine(mode: str = "FULL"):
    try:
        execution_log = run_engine_pipeline(mode)
        return {
            "status": "SUCCESS",
            "message": "Risk engine executed successfully",
            "execution_log": execution_log,
        }

    except EngineExecutionError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
