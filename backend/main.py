"""
NER-LIS Backend — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import roads, incidents, vehicles, shipments, routing, alerts, ml, auth

app = FastAPI(
    title="NER-LIS API",
    description="North Eastern Region – Logistics Intelligence System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["Auth"])
app.include_router(roads.router,     prefix="/api/v1/roads",     tags=["Roads"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(vehicles.router,  prefix="/api/v1/vehicles",  tags=["Vehicles"])
app.include_router(shipments.router, prefix="/api/v1/shipments", tags=["Shipments"])
app.include_router(routing.router,   prefix="/api/v1/routing",   tags=["Routing"])
app.include_router(alerts.router,    prefix="/api/v1/alerts",    tags=["Alerts"])
app.include_router(ml.router,        prefix="/api/v1/ml",        tags=["ML"])


@app.get("/", tags=["Health"])
async def root():
    return {"service": "NER-LIS API", "status": "running", "version": "0.1.0"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
