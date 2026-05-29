import time
from datetime import datetime, timezone
import logging

from src.scenario_portfolio_risk import run_scenario_risk
from src.risk_limits import run_risk_limits
from src.backtesting import run_backtesting
from src.stress_testing import run_stress_testing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EngineExecutionError(RuntimeError):
    pass

def run_engine_pipeline(mode: str = "FULL") -> dict:
    """
    Executes the risk engine pipeline sequentially in-process.
    Replaces the old subprocess approach for better performance and thread-safety.
    """
    execution_log = {
        "start_time": datetime.now(timezone.utc).isoformat(),
        "steps": [],
        "status": "RUNNING",
    }
    
    try:
        # Step 1: Scenario Generation & Portfolio Risk
        logger.info(f"Starting Scenario Risk Engine in {mode} mode")
        start_t = time.time()
        risk_metrics = run_scenario_risk(mode)
        execution_log["steps"].append({
            "script": "scenario_portfolio_risk",
            "duration_sec": round(time.time() - start_t, 2),
            "status": "SUCCESS"
        })
        
        # Step 2: Risk Limits Governance
        logger.info("Starting Risk Limits Check")
        start_t = time.time()
        limits_status = run_risk_limits()
        execution_log["steps"].append({
            "script": "risk_limits",
            "duration_sec": round(time.time() - start_t, 2),
            "status": "SUCCESS"
        })
        
        # Step 3: Rolling Backtesting
        logger.info("Starting Rolling Backtesting")
        start_t = time.time()
        backtest_results = run_backtesting()
        execution_log["steps"].append({
            "script": "backtesting",
            "duration_sec": round(time.time() - start_t, 2),
            "status": "SUCCESS"
        })
        
        # Step 4: Volatility Stress Testing
        logger.info("Starting Volatility Stress Testing")
        start_t = time.time()
        run_stress_testing(mode)
        execution_log["steps"].append({
            "script": "stress_testing",
            "duration_sec": round(time.time() - start_t, 2),
            "status": "SUCCESS"
        })
        
        execution_log["status"] = "SUCCESS"
        execution_log["end_time"] = datetime.now(timezone.utc).isoformat()
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        execution_log["status"] = "FAILED"
        execution_log["error"] = str(e)
        execution_log["end_time"] = datetime.now(timezone.utc).isoformat()
        raise EngineExecutionError(f"Engine failed: {str(e)}") from e
        
    return execution_log
