"""Supabase checkpointer for LangGraph state persistence."""
import asyncio
import logging
from typing import Any, Optional
from datetime import datetime
import json

from supabase import create_client, Client
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseCheckpointer(BaseCheckpointSaver):
    """Checkpointer that saves LangGraph state to Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
    
    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        """Async version of put for LangGraph compatibility."""
        return self.put(config, checkpoint, metadata)
    
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        """Save a checkpoint to Supabase.
        
        Args:
            config: Runnable configuration
            checkpoint: Checkpoint data to save
            metadata: Checkpoint metadata
            
        Returns:
            Updated config with checkpoint info
        """
        thread_id = config.get("configurable", {}).get("thread_id")
        checkpoint_id = checkpoint.get("id", str(datetime.utcnow().timestamp()))
        
        if not thread_id:
            logger.warning("No thread_id in config, cannot save checkpoint")
            return config
        
        try:
            # Serialize checkpoint data
            checkpoint_data = {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "checkpoint": json.dumps(checkpoint),
                "metadata": json.dumps(metadata) if metadata else None,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            # Insert into Supabase
            self.client.table("checkpoints").upsert(checkpoint_data).execute()
            
            logger.info(f"Saved checkpoint {checkpoint_id} for thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
        
        return config
    
    async def aget_tuple(self, config: RunnableConfig) -> Optional[tuple]:
        """Async version of get_tuple for LangGraph compatibility.
        
        Args:
            config: Runnable configuration with thread_id
            
        Returns:
            Tuple of (checkpoint, metadata) if found, None otherwise
        """
        checkpoint = self.get(config)
        if checkpoint:
            return (checkpoint, {})
        return None
    
    def get(self, config: RunnableConfig) -> Optional[Checkpoint]:
        """Retrieve the latest checkpoint for a thread.
        
        Args:
            config: Runnable configuration with thread_id
            
        Returns:
            Checkpoint if found, None otherwise
        """
        thread_id = config.get("configurable", {}).get("thread_id")
        
        if not thread_id:
            return None
        
        try:
            # Query latest checkpoint for thread
            result = (
                self.client.table("checkpoints")
                .select("*")
                .eq("thread_id", thread_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                checkpoint_row = result.data[0]
                checkpoint = json.loads(checkpoint_row["checkpoint"])
                logger.info(f"Retrieved checkpoint for thread {thread_id}")
                return checkpoint
            
        except Exception as e:
            logger.error(f"Failed to retrieve checkpoint: {e}")
        
        return None
    
    def list(self, config: RunnableConfig) -> list[Checkpoint]:
        """List all checkpoints for a thread.
        
        Args:
            config: Runnable configuration with thread_id
            
        Returns:
            List of checkpoints
        """
        thread_id = config.get("configurable", {}).get("thread_id")
        
        if not thread_id:
            return []
        
        try:
            result = (
                self.client.table("checkpoints")
                .select("*")
                .eq("thread_id", thread_id)
                .order("created_at", desc=True)
                .execute()
            )
            
            checkpoints = []
            for row in result.data:
                checkpoint = json.loads(row["checkpoint"])
                checkpoints.append(checkpoint)
            
            return checkpoints
            
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            return []
