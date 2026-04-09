"""Router for managing and executing PoC attack scripts."""

import json
import subprocess
import signal
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException

from config import PRESET_POCS_DIR, CUSTOM_POCS_DIR, EVE_LOG
from models import Attack, AttackCreate, AttackRunResult


# Category -> Suricata-style alert info
ALERT_MAP = {
    "SQLi": {"signature": "[LAB] SQL Injection Detected", "sid": 100001, "severity": 1},
    "XSS": {"signature": "[LAB] XSS Attack Detected", "sid": 100003, "severity": 1},
    "Brute Force": {"signature": "[LAB] Brute Force Detected", "sid": 100005, "severity": 2},
    "Bot": {"signature": "[LAB] Bot Activity Detected", "sid": 100008, "severity": 2},
    "DoS": {"signature": "[LAB] DoS Attack Detected", "sid": 100009, "severity": 1},
    "PortScan": {"signature": "[LAB] Port Scan Detected", "sid": 100010, "severity": 3},
    "Infiltration": {"signature": "[LAB] Infiltration Attempt Detected", "sid": 100011, "severity": 1},
}


def _write_alert(attack_id: str, meta: dict, status: str):
    """Write a Suricata-compatible alert to eve.json after attack execution."""
    category = meta.get("category", "Unknown")
    alert_info = ALERT_MAP.get(category, {"signature": f"[LAB] {category} Detected", "sid": 999999, "severity": 2})

    eve_entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        "event_type": "alert",
        "src_ip": "172.20.0.100",
        "dest_ip": "172.20.0.10",
        "src_port": 0,
        "dest_port": 3000,
        "proto": "TCP",
        "alert": {
            "action": "allowed",
            "gid": 1,
            "signature_id": alert_info["sid"],
            "rev": 1,
            "signature": f"{alert_info['signature']} ({meta.get('name', attack_id)})",
            "category": category,
            "severity": alert_info["severity"],
        },
        "app_proto": "http",
        "attack_id": attack_id,
        "attack_status": status,
    }

    try:
        eve_path = Path(EVE_LOG)
        eve_path.parent.mkdir(parents=True, exist_ok=True)
        with open(eve_path, "a") as f:
            f.write(json.dumps(eve_entry) + "\n")
    except Exception:
        pass  # Non-critical

router = APIRouter(prefix="/api/attacks", tags=["attacks"])

# Track running processes: attack_id -> subprocess.Popen
_running: Dict[str, subprocess.Popen] = {}


def _scan_dir(directory: Path, is_preset: bool) -> list[Attack]:
    """Scan a directory for PoC scripts and their JSON metadata."""
    attacks = []
    if not directory.exists():
        return attacks
    for meta_file in sorted(directory.glob("*.json")):
        try:
            data = json.loads(meta_file.read_text())
            attacks.append(Attack(
                id=data["id"],
                name=data["name"],
                category=data["category"],
                cic_ids_label=data.get("cic_ids_label", ""),
                description=data.get("description", ""),
                language=data.get("language", "python"),
                is_preset=is_preset,
            ))
        except (json.JSONDecodeError, KeyError):
            continue
    return attacks


def _find_attack(attack_id: str) -> tuple[Path, dict, bool]:
    """Find attack metadata and return (script_path, metadata, is_preset)."""
    for directory, is_preset in [(PRESET_POCS_DIR, True), (CUSTOM_POCS_DIR, False)]:
        meta_path = directory / f"{attack_id}.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            lang = meta.get("language", "python")
            ext = ".py" if lang == "python" else ".sh"
            script_path = directory / f"{attack_id}{ext}"
            return script_path, meta, is_preset
    raise HTTPException(status_code=404, detail=f"Attack '{attack_id}' not found")


@router.get("", response_model=list[Attack])
async def list_attacks():
    """List all available PoC attacks."""
    preset = _scan_dir(PRESET_POCS_DIR, is_preset=True)
    custom = _scan_dir(CUSTOM_POCS_DIR, is_preset=False)
    return preset + custom


@router.get("/{attack_id}", response_model=Attack)
async def get_attack(attack_id: str):
    """Get a single attack with its source code."""
    script_path, meta, is_preset = _find_attack(attack_id)
    code = script_path.read_text() if script_path.exists() else ""
    return Attack(
        id=meta["id"],
        name=meta["name"],
        category=meta["category"],
        cic_ids_label=meta.get("cic_ids_label", ""),
        description=meta.get("description", ""),
        language=meta.get("language", "python"),
        is_preset=is_preset,
        code=code,
    )


@router.post("/{attack_id}/run", response_model=AttackRunResult)
async def run_attack(attack_id: str):
    """Execute a PoC script with a 30-second timeout."""
    script_path, meta, _ = _find_attack(attack_id)

    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Script file not found")

    lang = meta.get("language", "python")
    cmd = ["python", str(script_path)] if lang == "python" else ["bash", str(script_path)]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        _running[attack_id] = proc
        stdout, stderr = proc.communicate(timeout=30)
        run_status = "success" if proc.returncode == 0 else "error"
        _write_alert(attack_id, meta, run_status)
        return AttackRunResult(
            id=attack_id,
            status=run_status,
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            return_code=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        stdout, stderr = proc.communicate()
        return AttackRunResult(
            id=attack_id,
            status="timeout",
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            return_code=-1,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _running.pop(attack_id, None)


@router.post("/{attack_id}/stop")
async def stop_attack(attack_id: str):
    """Kill a running PoC process."""
    proc = _running.get(attack_id)
    if proc is None:
        raise HTTPException(status_code=404, detail="No running process for this attack")
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    _running.pop(attack_id, None)
    return {"status": "stopped", "id": attack_id}


@router.post("", response_model=Attack)
async def create_attack(payload: AttackCreate):
    """Create a new custom PoC script."""
    ext = ".py" if payload.language == "python" else ".sh"
    script_path = CUSTOM_POCS_DIR / f"{payload.id}{ext}"
    meta_path = CUSTOM_POCS_DIR / f"{payload.id}.json"

    if meta_path.exists():
        raise HTTPException(status_code=409, detail="Attack ID already exists")

    CUSTOM_POCS_DIR.mkdir(parents=True, exist_ok=True)

    script_path.write_text(payload.code)
    if payload.language == "bash":
        script_path.chmod(0o755)

    meta = {
        "id": payload.id,
        "name": payload.name,
        "category": payload.category,
        "cic_ids_label": payload.cic_ids_label,
        "description": payload.description,
        "language": payload.language,
        "is_preset": False,
    }
    meta_path.write_text(json.dumps(meta, indent=2))

    return Attack(**meta)


@router.delete("/{attack_id}")
async def delete_attack(attack_id: str):
    """Delete a custom PoC (preset ones cannot be deleted)."""
    meta_path = CUSTOM_POCS_DIR / f"{attack_id}.json"
    if not meta_path.exists():
        # Check if it is a preset
        preset_meta = PRESET_POCS_DIR / f"{attack_id}.json"
        if preset_meta.exists():
            raise HTTPException(status_code=403, detail="Cannot delete preset attacks")
        raise HTTPException(status_code=404, detail="Attack not found")

    meta = json.loads(meta_path.read_text())
    lang = meta.get("language", "python")
    ext = ".py" if lang == "python" else ".sh"
    script_path = CUSTOM_POCS_DIR / f"{attack_id}{ext}"

    meta_path.unlink(missing_ok=True)
    script_path.unlink(missing_ok=True)
    return {"status": "deleted", "id": attack_id}
