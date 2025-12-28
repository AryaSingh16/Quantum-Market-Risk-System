import json
from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter()

LIMITS_FILE = Path("data") / "risk_limits.json"


@router.get("/results/limits")
def get_risk_limits():
    if not LIMITS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Risk limits not found. Run engine first.",
        )

    with open(LIMITS_FILE, "r") as f:
        return json.load(f)