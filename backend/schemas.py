from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str
    engine_available: bool
    message: Optional[str] = None
