"""Pydantic models for the API."""

from typing import Optional, List
from pydantic import BaseModel


class Attack(BaseModel):
    id: str
    name: str
    category: str
    cic_ids_label: str
    description: str
    language: str
    is_preset: bool
    code: Optional[str] = None


class AttackCreate(BaseModel):
    id: str
    name: str
    category: str
    cic_ids_label: str
    description: str
    language: str  # "python" or "bash"
    code: str


class AttackRunResult(BaseModel):
    id: str
    status: str  # "success", "error", "timeout"
    stdout: str
    stderr: str
    return_code: int


class Rule(BaseModel):
    sid: int
    enabled: bool
    raw: str
    msg: Optional[str] = None
    source_file: str  # "preset" or "custom"


class RuleCreate(BaseModel):
    raw: Optional[str] = None
    content: Optional[str] = None  # alias for raw (from frontend)
    name: Optional[str] = None
    category: Optional[str] = None

    def get_raw(self) -> str:
        return self.raw or self.content or ""


class Alert(BaseModel):
    timestamp: str
    src_ip: Optional[str] = None
    src_port: Optional[int] = None
    dest_ip: Optional[str] = None
    dest_port: Optional[int] = None
    proto: Optional[str] = None
    signature: Optional[str] = None
    signature_id: Optional[int] = None
    severity: Optional[int] = None
    category: Optional[str] = None


class AlertStats(BaseModel):
    signature: str
    count: int


class ServiceStatus(BaseModel):
    name: str
    status: str  # "up", "down", "unknown"
    detail: Optional[str] = None
