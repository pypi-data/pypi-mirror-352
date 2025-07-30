"""
Database utilities for agent core functionality.
"""
import asyncio
from typing import Optional, Dict, Any

import asyncpg


# Global connection pool
_pool: Optional[asyncpg.Pool] = None
_pool_lock = asyncio.Lock()


async def init_db_pool(db_url: str, **kwargs) -> asyncpg.Pool:
    """
    Initialize the database connection pool.
    
    Args:
        db_url: The database connection URL
        **kwargs: Additional arguments to pass to asyncpg.create_pool
        
    Returns:
        The connection pool
    """
    global _pool
    
    # Use a lock to prevent multiple initializations
    async with _pool_lock:
        if _pool is None:
            # Default pool settings
            pool_settings = {
                "min_size": 1,
                "max_size": 10,
                "command_timeout": 60.0,
                # Add any default settings here
            }
            
            # Update with user-provided settings
            pool_settings.update(kwargs)
            
            # Create the pool
            _pool = await asyncpg.create_pool(db_url, **pool_settings)
    
    return _pool


async def close_db_pool() -> None:
    """
    Close the database connection pool if it exists.
    """
    global _pool
    
    async with _pool_lock:
        if _pool is not None:
            await _pool.close()
            _pool = None


async def get_db_pool() -> asyncpg.Pool:
    """
    Get the current database connection pool.
    
    Returns:
        The connection pool
        
    Raises:
        RuntimeError: If the pool has not been initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool first.")
    
    return _pool 