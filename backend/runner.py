import os
import subprocess
import sys
from datetime import datetime, timezone
from backend.config import SRC_DIR


ENGINE_PIPELINE = [
    "scenario_portfolio_risk.py",
    "risk_limits.py",
    "backtesting.py",
]


class EngineExecutionError(RuntimeError):
    pass


env = os.environ.copy()
env["PYTHONPATH"] = str(SRC_DIR.parent)


def run_engine_pipeline(mode: str = "FULL") -> dict:
    env["QMC_MODE"] = mode
    """
    Executes the risk engine scripts sequentially.
    No imports. No refactoring. Subprocess only.
    """

    execution_log = {
        "start_time": datetime.now(timezone.utc).isoformat(),
        "steps": [],
        "status": "RUNNING",
    }

    for script in ENGINE_PIPELINE:
        script_path = SRC_DIR / script

        step_info = {
            "script": script,
            "start_time": datetime.utcnow().isoformat(),
            "return_code": None,
        }

        try:
            completed = subprocess.run(
                f'"{sys.executable}" "{script_path}"',
                shell=True,                     
                check=True,
                capture_output=True,
                text=True,
                cwd=str(SRC_DIR.parent),
                env=env,
            )


            step_info["return_code"] = completed.returncode
            step_info["stdout"] = completed.stdout
            step_info["stderr"] = completed.stderr
            step_info["status"] = "SUCCESS"

        except subprocess.CalledProcessError as e:
            step_info["return_code"] = e.returncode
            step_info["stdout"] = e.stdout
            step_info["stderr"] = e.stderr
            step_info["status"] = "FAILED"



            execution_log["steps"].append(step_info)
            execution_log["status"] = "FAILED"
            execution_log["end_time"] = datetime.now(timezone.utc).isoformat()

            raise EngineExecutionError(
                f"Engine failed at step: {script}"
            ) from e

        execution_log["steps"].append(step_info)

    execution_log["status"] = "SUCCESS"
    execution_log["end_time"] = datetime.utcnow().isoformat()
    return execution_log
