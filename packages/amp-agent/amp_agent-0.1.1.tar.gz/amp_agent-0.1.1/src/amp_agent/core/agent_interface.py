"""
Abstract agent interface for AMP agents.
This module defines the interface that all agent implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List

class AgentResponse:
    """
    Standard response format for all agent implementations.
    """
    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tools_used: Optional[List[Dict[str, Any]]] = None
    ):
        self.content = content
        self.metadata = metadata or {}
        self.tools_used = tools_used or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response to a dictionary.
        """
        return {
            "content": self.content,
            "metadata": self.metadata,
            "tools_used": self.tools_used
        }

class AgentInterface(ABC):
    """
    Abstract interface for all agent implementations.
    All agent implementations must inherit from this class and implement its methods.
    """
    def __init__(self, agent_config, core_config, session_id, user_id):
        self.agent_config = agent_config
        self.core_config = core_config
        self.session_id = session_id
        self.user_id = user_id
        
    @abstractmethod
    def run(self, input_content: str, metadata: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> AgentResponse:
        """
        Run the agent with the given input content.
        
        Args:
            input_content: The input content to process
            metadata: Additional metadata for the request
            dry_run: Whether to run in dry run mode (no LLM calls)
            
        Returns:
            An AgentResponse object containing the agent's response
        """
        pass
    
    @abstractmethod
    def get_agent_id(self) -> str:
        """
        Get the agent's ID.
        
        Returns:
            The agent's ID
        """
        pass
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """
        Get the agent's name.
        
        Returns:
            The agent's name
        """
        pass 