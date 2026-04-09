"""Router for managing Suricata rules."""

import re
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException

from config import PRESET_RULES_DIR, CUSTOM_RULES_DIR
from models import Rule, RuleCreate

router = APIRouter(prefix="/api/rules", tags=["rules"])

SID_RE = re.compile(r"sid\s*:\s*(\d+)")
MSG_RE = re.compile(r'msg\s*:\s*"([^"]*)"')


def _parse_rules_file(filepath: Path, source: str) -> list[Rule]:
    """Parse a .rules file into Rule objects."""
    rules = []
    if not filepath.exists():
        return rules
    for line in filepath.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") and not SID_RE.search(stripped):
            continue  # skip blanks and pure comments
        enabled = not stripped.startswith("#")
        raw = stripped.lstrip("# ") if not enabled else stripped
        sid_match = SID_RE.search(raw)
        msg_match = MSG_RE.search(raw)
        if sid_match:
            rules.append(Rule(
                sid=int(sid_match.group(1)),
                enabled=enabled,
                raw=raw,
                msg=msg_match.group(1) if msg_match else None,
                source_file=source,
            ))
    return rules


def _get_all_rules() -> list[Rule]:
    """Get rules from all files."""
    rules = []
    for rf in sorted(PRESET_RULES_DIR.glob("*.rules")):
        rules.extend(_parse_rules_file(rf, "preset"))
    for rf in sorted(CUSTOM_RULES_DIR.glob("*.rules")):
        rules.extend(_parse_rules_file(rf, "custom"))
    return rules


def _toggle_in_file(filepath: Path, sid: int, enable: bool):
    """Comment or uncomment a rule line by SID."""
    if not filepath.exists():
        return False
    lines = filepath.read_text().splitlines()
    found = False
    new_lines = []
    for line in lines:
        if SID_RE.search(line) and int(SID_RE.search(line).group(1)) == sid:
            found = True
            stripped = line.lstrip("# ")
            if enable:
                new_lines.append(stripped)
            else:
                new_lines.append("# " + stripped)
        else:
            new_lines.append(line)
    if found:
        filepath.write_text("\n".join(new_lines) + "\n")
    return found


def _reload_suricata():
    """Send SIGUSR2 to Suricata to reload rules."""
    try:
        result = subprocess.run(
            ["docker", "exec", "suricata", "kill", "-USR2", "1"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


@router.get("", response_model=list[Rule])
async def list_rules():
    """List all Suricata rules."""
    return _get_all_rules()


@router.put("/{sid}/toggle")
async def toggle_rule(sid: int, enable: bool = True):
    """Enable or disable a rule by SID."""
    toggled = False
    for rf in PRESET_RULES_DIR.glob("*.rules"):
        if _toggle_in_file(rf, sid, enable):
            toggled = True
            break
    if not toggled:
        for rf in CUSTOM_RULES_DIR.glob("*.rules"):
            if _toggle_in_file(rf, sid, enable):
                toggled = True
                break
    if not toggled:
        raise HTTPException(status_code=404, detail=f"Rule SID {sid} not found")

    _reload_suricata()
    return {"status": "toggled", "sid": sid, "enabled": enable}


@router.post("", response_model=Rule)
async def create_rule(payload: RuleCreate):
    """Add a new custom rule."""
    CUSTOM_RULES_DIR.mkdir(parents=True, exist_ok=True)
    custom_file = CUSTOM_RULES_DIR / "custom.rules"

    rule_text = payload.get_raw()
    if not rule_text:
        raise HTTPException(status_code=400, detail="Rule content is required (raw or content field)")

    sid_match = SID_RE.search(rule_text)
    if not sid_match:
        raise HTTPException(status_code=400, detail="Rule must contain a 'sid' field")

    sid = int(sid_match.group(1))
    msg_match = MSG_RE.search(rule_text)

    # Append to custom rules file
    with open(custom_file, "a") as f:
        f.write(rule_text.strip() + "\n")

    _reload_suricata()

    return Rule(
        sid=sid,
        enabled=True,
        raw=rule_text.strip(),
        msg=msg_match.group(1) if msg_match else None,
        source_file="custom",
    )


@router.delete("/{sid}")
async def delete_rule(sid: int):
    """Delete a custom rule by SID."""
    custom_file = CUSTOM_RULES_DIR / "custom.rules"
    if not custom_file.exists():
        raise HTTPException(status_code=404, detail="No custom rules file")

    lines = custom_file.read_text().splitlines()
    new_lines = []
    found = False
    for line in lines:
        m = SID_RE.search(line)
        if m and int(m.group(1)) == sid:
            found = True
            continue
        new_lines.append(line)

    if not found:
        raise HTTPException(status_code=404, detail=f"Custom rule SID {sid} not found")

    custom_file.write_text("\n".join(new_lines) + "\n")
    _reload_suricata()
    return {"status": "deleted", "sid": sid}


@router.post("/reload")
async def reload_rules():
    """Reload Suricata rules."""
    success = _reload_suricata()
    return {"status": "reloaded" if success else "failed"}
