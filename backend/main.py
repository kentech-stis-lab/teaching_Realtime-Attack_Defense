"""FastAPI backend for Red/Blue Team Lab."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import attacks, rules, monitor

app = FastAPI(
    title="Red/Blue Team Lab API",
    description="Backend API for managing PoC attacks, Suricata rules, and monitoring",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attacks.router)
app.include_router(rules.router)
app.include_router(monitor.router)


@app.get("/")
async def root():
    return {
        "service": "Red/Blue Team Lab API",
        "version": "1.0.0",
        "docs": "/docs",
    }
