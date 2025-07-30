"""
Configuration management for agent core functionality.
"""
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv


def load_core_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load core configuration from environment variables.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load environment variables from .env file if provided
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    # Required environment variables
    required_vars = ["SUPABASE_DB_URL", "AMP_JWKS_URL", "OPENAI_API_KEY"]
    # required_vars = required_vars + ["SUPABASE_URL", "SUPABASE_ANON_KEY"] ## Added for subscription
    
    # Check for required environment variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Build configuration dictionary
    config = {
        "db_url": os.getenv("SUPABASE_DB_URL"),
        "jwks_url": os.getenv("AMP_JWKS_URL"),
        "openai_api_key": os.getenv("OPENAI_API_KEY", "").strip(),
        # "supabase_url": os.getenv("SUPABASE_URL"),
        # "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY"),
    }
    
    # Add optional configuration
    if os.getenv("LOG_LEVEL"):
        config["log_level"] = os.getenv("LOG_LEVEL")
    
    return config 