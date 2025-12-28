from fastapi import FastAPI
from backend.routes import health, run, results, limits

app = FastAPI(
    title="Quantum–Classical Market Risk API",
    description="Production-style wrapper for portfolio VaR/CVaR engine",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(run.router)
app.include_router(results.router)
app.include_router(limits.router)