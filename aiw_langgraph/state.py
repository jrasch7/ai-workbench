"""aiw_langgraph.state

Defines the RunState dataclass representing the metadata for a LangGraph run.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class RunState:
    id: str
    title: str
    status: str  # queued|running|succeeded|failed|cancelled|timed_out
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    task_path: Optional[str] = None
    log_path: Optional[str] = None
    exit_code: Optional[int] = None
    pid: Optional[int] = None
    timeout_seconds: int = 1800
    cancel_requested: bool = False
    last_log_size: int = 0
    error: Optional[str] = None
    # Additional fields from original implementation
    level: Optional[str] = None
    llm_enabled: Optional[bool] = None
    llm_status: Optional[str] = None
    model: Optional[str] = None
    doc_status: Optional[str] = None
    generated_file: Optional[str] = None
