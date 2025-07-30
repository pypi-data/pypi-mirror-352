"""
Adapter for the process_message function to implement the AgentInterface.
"""
from typing import Dict, Any, Optional, Callable
import logging

from amp_agent.core.agent_interface import AgentInterface, AgentResponse

logger = logging.getLogger(__name__)

class ProcessMessageAdapter(AgentInterface):
    """
    Adapter for the process_message function to implement the AgentInterface.
    """
    
    def __init__(
        self,
        process_message_func: Callable[[str], str],
        agent_id: str,
        agent_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the adapter with a process_message function.
        
        Args:
            process_message_func: A function that takes a string input and returns a string response
            agent_id: The agent's ID
            agent_name: The agent's name
            metadata: Optional metadata for the agent
        """
        self._process_message_func = process_message_func
        self._agent_id = agent_id
        self._agent_name = agent_name
        self._metadata = metadata or {}
    
    def run(self, input_content: str, metadata: Dict[str, Any] = None) -> AgentResponse:
        """
        Run the process_message function with the given input content.
        
        Args:
            input_content: The input content to process
            
        Returns:
            An AgentResponse object containing the agent's response
        """
        # Run the process_message function
        response_content = self._process_message_func(input_content)
        
        # Create and return an AgentResponse
        return AgentResponse(
            content=response_content,
            metadata=self._metadata
        )
    
    def get_agent_id(self) -> str:
        """
        Get the agent's ID.
        
        Returns:
            The agent's ID
        """
        return self._agent_id
    
    def get_agent_name(self) -> str:
        """
        Get the agent's name.
        
        Returns:
            The agent's name
        """
        return self._agent_name 