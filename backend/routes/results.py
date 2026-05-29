import numpy as np
from fastapi import APIRouter, HTTPException
from src.engine.database import get_connection
from backend.config import RISK_STATE_FILE, FIGURES_DIR

router = APIRouter()

@router.get("/results/summary")
def results_summary():
    if not RISK_STATE_FILE.exists():
        raise HTTPException(status_code=404, detail="Risk state not found")

    data = np.load(RISK_STATE_FILE)

    return {
        "portfolio": {
            "quantum": {
                "VaR": float(data["q_port_VaR"]),
                "CVaR": float(data["q_port_CVaR"]),
                "MVaR": data["q_mvar"].tolist(),
                "ComponentVaR": data["q_comp_var"].tolist(),
            },
            "classical": {
                "VaR": float(data["c_port_VaR"]),
                "CVaR": float(data["c_port_CVaR"]),
            },
        },
        "tickers": data["tickers"].tolist() if "tickers" in data else []
    }


@router.get("/results/arrays")
def results_arrays():
    if not RISK_STATE_FILE.exists():
        raise HTTPException(status_code=404, detail="Risk state not found")

    data = np.load(RISK_STATE_FILE)

    return {
        "portfolio_returns_quantum": data["portfolio_returns_q"].tolist(),
        "portfolio_returns_classical": data["portfolio_returns_c"].tolist(),
    }


@router.get("/results/figures")
def results_figures():
    if not FIGURES_DIR.exists():
        raise HTTPException(status_code=404, detail="Figures directory missing")

    return {
        "available_figures": sorted(
            f.name for f in FIGURES_DIR.glob("*.png")
        )
    }

@router.get("/results/backtest")
def results_backtest():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM backtest_results ORDER BY timestamp DESC LIMIT 1')
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="No backtest results found")
        
    col_names = [description[0] for description in cursor.description]
    conn.close()
    
    return dict(zip(col_names, row))
