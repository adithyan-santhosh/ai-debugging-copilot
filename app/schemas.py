from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class IssueSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    service: Optional[str] = None
    context: Optional[dict] = None


class APITrace(BaseModel):
    path: str
    method: str
    status_code: int
    latency_ms: Optional[float] = None
    request: Optional[dict] = None
    response: Optional[dict] = None
    error: Optional[str] = None


class DBQuery(BaseModel):
    query: str
    duration_ms: Optional[float] = None
    database: Optional[str] = None
    collection: Optional[str] = None
    error: Optional[str] = None


class IngestResponse(BaseModel):
    accepted: int
    message: str


class IssueDetail(BaseModel):
    id: str
    category: str
    severity: IssueSeverity
    title: str
    root_cause: str
    suggested_fix: str
    evidence: List[str]
    optimization: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AnalyzeRequest(BaseModel):
    include_logs: bool = Field(default=True)
    include_api_traces: bool = Field(default=True)
    include_db_queries: bool = Field(default=True)
