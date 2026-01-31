"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Shadow Twin Guardian Orchestrator starting up...")
    logger.info(f"Supabase URL: {settings.supabase_url}")
    logger.info(f"Ollama endpoint: {settings.ollama_base_url}")
    yield
    logger.info("Shadow Twin Guardian Orchestrator shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Shadow Twin Guardian",
    description="Multi-agent orchestration for e-commerce migration parity testing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Shadow Twin Guardian",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.orchestrator_host,
        port=settings.orchestrator_port,
        reload=True,
    )
