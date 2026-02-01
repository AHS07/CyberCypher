"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class Verdict(str, Enum):
    """Final verdict from council."""
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class CouncilOpinion(BaseModel):
    """Opinion from a single council member."""
    agent: str = Field(..., description="Agent name (primary_analyzer, skeptic_critic, consensus_judge)")
    provider: str = Field(..., description="LLM provider used (huggingface)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis: str = Field(..., description="Detailed analysis text")
    detected_issues: list[str] = Field(default_factory=list)
    false_positives: list[str] = Field(default_factory=list)
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score from 0.0 to 1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in assessment")


class AnalyzeRequest(BaseModel):
    """Request to analyze a parity test."""
    test_id: str = Field(..., description="Unique test identifier")
    merchant_id: str = Field(..., description="Merchant identifier")
    legacy_response: dict[str, Any] = Field(..., description="Legacy API response")
    headless_response: dict[str, Any] = Field(..., description="Headless API response")
    diff_report: dict[str, Any] = Field(..., description="DeepDiff report")


class AnalyzeResponse(BaseModel):
    """Response from analysis request."""
    test_id: str
    status: TestStatus
    message: str


class TestStatusResponse(BaseModel):
    """Current status of a test."""
    test_id: str
    merchant_id: str
    status: TestStatus
    active_provider: str
    providers_attempted: list[str]
    council_opinions: list[CouncilOpinion]
    risk_score: Optional[float] = None
    final_verdict: Optional[Verdict] = None
    is_mitigated: bool = False
    mitigation_recommendation: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProviderHealth(BaseModel):
    """Health status of an LLM provider."""
    provider: str
    is_healthy: bool
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    avg_response_time_ms: Optional[float] = None


class ReliabilityLog(BaseModel):
    """Log entry for provider reliability tracking."""
    id: str
    test_id: str
    provider: str
    event_type: str  # "success", "failure", "failover"
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    failover_to: Optional[str] = None
    response_time_ms: Optional[float] = None
    timestamp: datetime
