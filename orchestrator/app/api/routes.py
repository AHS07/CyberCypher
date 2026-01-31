"""FastAPI routes for Shadow Twin Guardian."""
import logging
import asyncio
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from supabase import create_client

from app.core.config import settings
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    TestStatusResponse,
    TestStatus,
    ProviderHealth,
)
from app.graph.council_graph import run_council_analysis
from app.core.llm_manager import llm_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Supabase client
supabase = create_client(settings.supabase_url, settings.supabase_service_key)

# Active WebSocket connections
active_connections: Dict[str, list[WebSocket]] = {}


async def process_analysis(request: AnalyzeRequest):
    """Background task to process analysis and update database."""
    try:
        logger.info(f"Processing analysis for test {request.test_id}")
        
        # Update status to analyzing
        supabase.table("shadow_tests").update({
            "status": "analyzing",
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("test_id", request.test_id).execute()
        
        # Run council analysis using mock council (fallback when Ollama unavailable)
        from app.mock_council import mock_council
        final_state = await mock_council.analyze_diff(
            test_id=request.test_id,
            merchant_id=request.merchant_id,
            diff_report=request.diff_report,
            legacy_response=request.legacy_response,
            headless_response=request.headless_response,
        )
        
        # Update database with final results
        supabase.table("shadow_tests").update({
            "status": final_state["status"],
            "council_opinions": final_state["council_opinions"],
            "active_provider": final_state["active_provider"],
            "risk_score": final_state.get("risk_score"),
            "final_verdict": final_state.get("final_verdict"),
            "is_mitigated": final_state["is_mitigated"],
            "mitigation_recommendation": final_state.get("mitigation_recommendation"),
            "error_message": final_state.get("error_message"),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("test_id", request.test_id).execute()
        
        logger.info(f"Analysis completed for test {request.test_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for test {request.test_id}: {e}")
        
        # Update database with error
        supabase.table("shadow_tests").update({
            "status": "failed",
            "error_message": str(e),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("test_id", request.test_id).execute()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_parity_test(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger analysis of a parity test.
    
    This endpoint:
    1. Creates a new test record in the database
    2. Triggers the council analysis in the background
    3. Returns immediately with test_id and status
    
    The actual analysis runs asynchronously and updates the database.
    Clients can poll /status/{test_id} or use WebSocket for real-time updates.
    """
    try:
        # Insert initial test record
        supabase.table("shadow_tests").insert({
            "test_id": request.test_id,
            "merchant_id": request.merchant_id,
            "diff_report": request.diff_report,
            "legacy_response": request.legacy_response,
            "headless_response": request.headless_response,
            "status": "pending",
            "council_opinions": [],
            "is_mitigated": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
        
        # Trigger background analysis
        background_tasks.add_task(process_analysis, request)
        
        return AnalyzeResponse(
            test_id=request.test_id,
            status=TestStatus.PENDING,
            message="Analysis started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{test_id}", response_model=TestStatusResponse)
async def get_test_status(test_id: str):
    """Get current status of a test."""
    try:
        result = supabase.table("shadow_tests").select("*").eq("test_id", test_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Test not found")
        
        test_data = result.data[0]
        
        return TestStatusResponse(
            test_id=test_data["test_id"],
            merchant_id=test_data["merchant_id"],
            status=TestStatus(test_data["status"]),
            active_provider=test_data.get("active_provider", ""),
            providers_attempted=test_data.get("providers_attempted", []),
            council_opinions=test_data.get("council_opinions", []),
            risk_score=test_data.get("risk_score"),
            final_verdict=test_data.get("final_verdict"),
            is_mitigated=test_data.get("is_mitigated", False),
            mitigation_recommendation=test_data.get("mitigation_recommendation"),
            error_message=test_data.get("error_message"),
            created_at=datetime.fromisoformat(test_data["created_at"]),
            updated_at=datetime.fromisoformat(test_data["updated_at"]),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get test status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/providers", response_model=list[ProviderHealth])
async def get_provider_health():
    """Get health status of all LLM providers."""
    health_data = []
    
    for provider, health in llm_manager.provider_health.items():
        health_data.append(ProviderHealth(
            provider=provider,
            is_healthy=health["is_healthy"],
            last_success=health.get("last_check"),
            consecutive_failures=health["consecutive_failures"],
        ))
    
    return health_data


@router.websocket("/ws/tests/{test_id}")
async def websocket_test_updates(websocket: WebSocket, test_id: str):
    """WebSocket endpoint for real-time test updates."""
    await websocket.accept()
    
    # Add to active connections
    if test_id not in active_connections:
        active_connections[test_id] = []
    active_connections[test_id].append(websocket)
    
    try:
        # Send initial status
        result = supabase.table("shadow_tests").select("*").eq("test_id", test_id).execute()
        if result.data and len(result.data) > 0:
            await websocket.send_json(result.data[0])
        
        # Keep connection alive and listen for updates
        while True:
            # Poll for updates every 2 seconds
            await asyncio.sleep(2)
            result = supabase.table("shadow_tests").select("*").eq("test_id", test_id).execute()
            if result.data and len(result.data) > 0:
                await websocket.send_json(result.data[0])
                
                # Close connection if test is complete or failed
                if result.data[0]["status"] in ["complete", "failed"]:
                    break
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for test {test_id}")
    finally:
        # Remove from active connections
        if test_id in active_connections:
            active_connections[test_id].remove(websocket)
            if len(active_connections[test_id]) == 0:
                del active_connections[test_id]


@router.post("/mitigate/{test_id}")
async def mitigate_test(test_id: str):
    """Mark a test as mitigated (human-in-the-loop action)."""
    try:
        result = supabase.table("shadow_tests").update({
            "is_mitigated": True,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("test_id", test_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Test not found")
        
        return {"message": "Test marked as mitigated", "test_id": test_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mitigate test: {e}")
        raise HTTPException(status_code=500, detail=str(e))
