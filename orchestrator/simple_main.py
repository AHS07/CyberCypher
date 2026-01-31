"""Simplified FastAPI application for testing."""
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Create FastAPI app
app = FastAPI(
    title="Shadow Twin Guardian - Simple",
    description="Simplified orchestrator for testing",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class AnalyzeRequest(BaseModel):
    test_id: str
    merchant_id: str
    legacy_response: Dict[str, Any]
    headless_response: Dict[str, Any]
    diff_report: Dict[str, Any]

@app.get("/")
async def root():
    return {"service": "Shadow Twin Guardian - Simple", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze_parity_test(request: AnalyzeRequest):
    """Simplified analysis endpoint using mock council."""
    try:
        logger.info(f"Received analysis request for test {request.test_id}")
        
        # Check if test already exists
        existing = supabase.table("shadow_tests").select("*").eq("test_id", request.test_id).execute()
        
        if not existing.data:
            # Insert initial test record
            supabase.table("shadow_tests").insert({
                "test_id": request.test_id,
                "merchant_id": request.merchant_id,
                "diff_report": request.diff_report,
                "legacy_response": request.legacy_response,
                "headless_response": request.headless_response,
                "status": "analyzing",
                "council_opinions": [],
                "is_mitigated": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()
        else:
            # Update existing record
            supabase.table("shadow_tests").update({
                "status": "analyzing",
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("test_id", request.test_id).execute()
        
        # Simple mock analysis
        issues = []
        risk_score = 0.0
        
        if "type_changes" in request.diff_report:
            issues.append("Type mismatch detected")
            risk_score += 0.3
        
        if "dictionary_item_removed" in request.diff_report:
            issues.append("Missing fields in headless response")
            risk_score += 0.4
            
        if "values_changed" in request.diff_report:
            issues.append("Value differences found")
            risk_score += 0.2
        
        # Determine verdict
        if risk_score < 0.3:
            verdict = "PASS"
            recommendation = "No significant issues detected."
        elif risk_score < 0.7:
            verdict = "NEEDS_REVIEW"
            recommendation = "Some issues detected. Manual review recommended."
        else:
            verdict = "FAIL"
            recommendation = "Critical issues found. Do not deploy."
        
        # Mock council opinions
        council_opinions = [
            {
                "agent": "primary_analyzer",
                "analysis": f"Detected {len(issues)} issues",
                "detected_issues": issues,
                "risk_score": risk_score,
                "confidence": 0.85
            }
        ]
        
        # Update database with results
        supabase.table("shadow_tests").update({
            "status": "complete",
            "council_opinions": council_opinions,
            "risk_score": risk_score,
            "final_verdict": verdict,
            "is_mitigated": False,
            "mitigation_recommendation": recommendation,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("test_id", request.test_id).execute()
        
        logger.info(f"Analysis completed for test {request.test_id}")
        
        return {
            "test_id": request.test_id,
            "status": "complete",
            "message": "Analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        
        # Update database with error
        try:
            supabase.table("shadow_tests").update({
                "status": "failed",
                "error_message": str(e),
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("test_id", request.test_id).execute()
        except:
            pass
        
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8003, reload=True)