from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.init_db import init_db
from app.api import (
    auth, alerts, incidents, responses, policies, 
    approvals, trust, outcomes, experience, metrics, system
)
from app.api import simulation

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Auto-start simulation engine on startup for live demo
    from app.services.network_simulator import network_simulator
    network_simulator.start()
    yield
    # Graceful shutdown
    network_simulator.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Trust-Aware SOAR for Adaptive Cybersecurity Response and Dynamic Autonomy",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(incidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(responses.router, prefix=settings.API_V1_PREFIX)
app.include_router(policies.router, prefix=settings.API_V1_PREFIX)
app.include_router(approvals.router, prefix=settings.API_V1_PREFIX)
app.include_router(trust.router, prefix=settings.API_V1_PREFIX)
app.include_router(outcomes.router, prefix=settings.API_V1_PREFIX)
app.include_router(experience.router, prefix=settings.API_V1_PREFIX)
app.include_router(metrics.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulation.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "message": "Trust-Aware SOAR Decision & Autonomy Platform",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "simulation": f"{settings.API_V1_PREFIX}/simulation/status"
    }
