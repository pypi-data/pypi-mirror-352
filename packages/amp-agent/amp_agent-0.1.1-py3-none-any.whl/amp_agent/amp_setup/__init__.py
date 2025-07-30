"""
AMP Setup - Configuration and setup utilities for AMP agents.
"""

from .auth_manager import get_auth_token, generate_api_key, AgentRegistrationError
from .config_manager import ConfigManager
from .platform_manager import PlatformManager
from .register_agents import register_agent, register_agents

__all__ = [
    # Auth utilities
    "get_auth_token",
    "generate_api_key",
    "AgentRegistrationError",
    
    # Managers
    "ConfigManager",
    "PlatformManager",
    
    # Registration utilities
    "register_agent",
    "register_agents",
]
