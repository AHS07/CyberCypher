"""Shared Python type definitions."""
from typing import TypedDict, Literal, Any
from datetime import datetime


TestStatus = Literal["pending", "analyzing", "complete", "failed"]
Verdict = Literal["PASS", "FAIL", "NEEDS_REVIEW"]
EventType = Literal["success", "failure", "failover"]
Provider = Literal["claude", "gemini", "ollama"]


class ShadowTestDB(TypedDict):
    """Shadow test record from database."""
    id: int
    test_id: str
    merchant_id: str
    diff_report: dict[str, Any]
    legacy_response: dict[str, Any]
    headless_response: dict[str, Any]
    council_opinions: list[dict[str, Any]]
    active_provider: str
    providers_attempted: list[str]
    is_mitigated: bool
    risk_score: float
    final_verdict: Verdict
    mitigation_recommendation: str
    status: TestStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime
