"""
Core functionality for AMP Agent.
"""

from .server import AgentServer, create_app
from .api import (
    get_api_key,
    create_a2c_token,
    send_messages,
    create_channels,
    list_channels,
    list_channel_agents
)
from .models import (
    AgentMessage,
    AgentResponse,
    MessagePart,
    Sender,
    Recipient,
    MessageHistory
)
from .agent_interface import AgentInterface
from .auth import validate_token
from .config import load_core_config
from .logging import logger, setup_logging

__version__ = "0.1.0"

__all__ = [
    # Server components
    "AgentServer",
    "create_app",
    
    # API functions
    "get_api_key",
    "create_a2c_token",
    "send_messages",
    "create_channels",
    "list_channels",
    "list_channel_agents",
    
    # Models
    "AgentMessage",
    "AgentResponse",
    "MessagePart",
    "Sender",
    "Recipient",
    "MessageHistory",
    
    # Core components
    "AgentInterface",
    "validate_token",
    "load_core_config",
    "logger",
    "setup_logging"
] 