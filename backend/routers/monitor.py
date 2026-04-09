"""Router for real-time monitoring, alerts, and service status."""

import asyncio
import json
import os
from collections import Counter
from pathlib import Path

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import EVE_LOG, SERVICE_URLS
from models import Alert, AlertStats, ServiceStatus

router = APIRouter(tags=["monitor"])


def _read_alerts(limit: int = 100) -> list[dict]:
    """Read the last N alert entries from eve.json."""
    eve_path = Path(EVE_LOG)
    if not eve_path.exists():
        return []

    alerts = []
    try:
        with open(eve_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("event_type") == "alert":
                        alert_info = entry.get("alert", {})
                        alerts.append({
                            "timestamp": entry.get("timestamp", ""),
                            "src_ip": entry.get("src_ip"),
                            "src_port": entry.get("src_port"),
                            "dest_ip": entry.get("dest_ip"),
                            "dest_port": entry.get("dest_port"),
                            "proto": entry.get("proto"),
                            "signature": alert_info.get("signature"),
                            "signature_id": alert_info.get("signature_id"),
                            "severity": alert_info.get("severity"),
                            "category": alert_info.get("category"),
                        })
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return alerts[-limit:]


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint that tails eve.json and streams alerts."""
    await websocket.accept()

    eve_path = Path(EVE_LOG)

    # Wait for file to exist
    for _ in range(30):
        if eve_path.exists():
            break
        await asyncio.sleep(1)

    if not eve_path.exists():
        await websocket.send_json({"error": "eve.json not found"})
        await websocket.close()
        return

    try:
        with open(eve_path, "r") as f:
            # Seek to end
            f.seek(0, os.SEEK_END)

            ping_counter = 0
            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    ping_counter += 1
                    # Send ping every 15 seconds to keep connection alive
                    if ping_counter >= 30:
                        try:
                            await websocket.send_json({"type": "ping"})
                        except Exception:
                            break
                        ping_counter = 0
                    continue

                ping_counter = 0
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    if entry.get("event_type") == "alert":
                        alert_info = entry.get("alert", {})
                        alert_data = {
                            "timestamp": entry.get("timestamp", ""),
                            "src_ip": entry.get("src_ip"),
                            "src_port": entry.get("src_port"),
                            "dest_ip": entry.get("dest_ip"),
                            "dest_port": entry.get("dest_port"),
                            "proto": entry.get("proto"),
                            "signature": alert_info.get("signature"),
                            "signature_id": alert_info.get("signature_id"),
                            "severity": alert_info.get("severity"),
                            "category": alert_info.get("category"),
                        }
                        await websocket.send_json(alert_data)
                except json.JSONDecodeError:
                    continue

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass


@router.get("/api/alerts", response_model=list[Alert])
async def get_alerts(limit: int = 100):
    """Get the last N alerts from eve.json."""
    return _read_alerts(limit)


@router.delete("/api/alerts")
async def clear_alerts():
    """Clear all alerts from eve.json (keep non-alert entries)."""
    eve_path = Path(EVE_LOG)
    if not eve_path.exists():
        return {"status": "ok", "cleared": 0}

    kept = []
    cleared = 0
    try:
        with open(eve_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("event_type") == "alert":
                        cleared += 1
                    else:
                        kept.append(line)
                except json.JSONDecodeError:
                    kept.append(line)

        with open(eve_path, "w") as f:
            for line in kept:
                f.write(line + "\n")
    except Exception:
        pass

    return {"status": "ok", "cleared": cleared}


@router.get("/api/alerts/stats", response_model=list[AlertStats])
async def get_alert_stats():
    """Get alert counts grouped by signature."""
    alerts = _read_alerts(limit=10000)
    counter = Counter(a.get("signature", "unknown") for a in alerts)
    return [
        AlertStats(signature=sig, count=cnt)
        for sig, cnt in counter.most_common()
    ]


@router.get("/api/status", response_model=list[ServiceStatus])
async def get_status():
    """Check health of all services."""
    statuses = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        # HTTP services
        for name, url in SERVICE_URLS.items():
            if url.startswith("http"):
                try:
                    health_url = url.rstrip("/") + "/health" if "internal-api" in name else url
                    resp = await client.get(health_url)
                    statuses.append(ServiceStatus(
                        name=name,
                        status="up" if resp.status_code < 500 else "down",
                        detail=f"HTTP {resp.status_code}",
                    ))
                except Exception as e:
                    statuses.append(ServiceStatus(
                        name=name,
                        status="down",
                        detail=str(e)[:100],
                    ))
            else:
                # TCP services - just report based on Docker
                statuses.append(ServiceStatus(
                    name=name,
                    status="unknown",
                    detail="TCP service - check via Docker",
                ))

    # Add suricata status
    try:
        eve_path = Path(EVE_LOG)
        if eve_path.exists() and eve_path.stat().st_size > 0:
            statuses.append(ServiceStatus(
                name="suricata",
                status="up",
                detail="eve.json is being written",
            ))
        else:
            statuses.append(ServiceStatus(
                name="suricata",
                status="unknown",
                detail="eve.json not found or empty",
            ))
    except Exception:
        statuses.append(ServiceStatus(
            name="suricata",
            status="unknown",
            detail="Could not check eve.json",
        ))

    return statuses
