from fastapi import APIRouter
from backend.schemas import HealthResponse
from backend.config import SRC_DIR

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    required_files = [
        "scenario_portfolio_risk.py",
        "risk_limits.py",
        "backtesting.py",
    ]

    missing = [f for f in required_files if not (SRC_DIR / f).exists()]

    if missing:
        return HealthResponse(
            status="ERROR",
            engine_available=False,
            message=f"Missing engine files: {missing}",
        )

    return HealthResponse(
        status="OK",
        engine_available=True,
        message="Risk engine files detected",
    )
