"""
Enhanced adapter for Agno agents with posting capabilities.
"""
from typing import Dict, Any, List, Optional

from amp_agent.core.agent_interface import AgentInterface, AgentResponse
from amp_agent.core.api import get_api_key, create_a2c_token, send_messages
from amp_agent.semantic.interest import check_agent_interest
from amp_agent.core.logging import logger


class AgnoAgentAdapter(AgentInterface):
    """
    Adapter for Agno agents to implement the AgentInterface.
    """
    
    def __init__(self, agno_agent, agent_config, core_config, session_id, user_id):
        super().__init__(agent_config, core_config, session_id, user_id)
        self._agno_agent = agno_agent
        self._agent_id = agno_agent.agent_id
        self._agent_name = agno_agent.name
        self._channel_id = agent_config.get("subscription_channels", [""])[0]
        
    def post_message(self, message: str, channel_id: str = None, mentions: List[str] = None) -> Dict[str, Any]:
        """
        Post a message to the channel.
        
        Args:
            message: The message to post
            channel_id: Optional channel ID to override default
            mentions: Optional list of agent IDs to mention
            
        Returns:
            Result of the send_messages call
        """
        # Skip if message is None or empty
        if not message:
            logger.info(f"\033[1;3m{self._agent_name}\033[0m skipping post for empty message")
            return {"error": "Empty message"}
            
        # Use provided channel ID or default
        active_channel = channel_id or self._channel_id
        if not active_channel:
            logger.error(f"\033[1;3m{self._agent_name}\033[0m No channel ID available for posting")
            return {"error": "No channel ID available"}
            
        # Default mentions to empty list
        mentions = mentions or []
        
        # Get API token and create A2C token
        api_token = get_api_key()
        a2c_token = create_a2c_token(self._agent_id, active_channel, api_token)
        
        # Log posting attempt
        logger.info(f"\033[1;3m{self._agent_name}\033[0m preparing to post message: {message[:50]}...")
        
        # Send the message
        result = send_messages(a2c_token, active_channel, message, mentions)
        
        # Log result
        if "error" in result:
            logger.error(f"\033[1;3m{self._agent_name}\033[0m message delivery failed: {result['error']}")
        else:
            message_id = result.get("id", "unknown")
            logger.info(f"\033[1;3m{self._agent_name}\033[0m message delivered successfully with ID: {message_id}")
            
        return result
        
    def run(self, input_content: str, metadata: Dict[str, Any] = None, dry_run: bool = False) -> AgentResponse:
        """
        Run the Agno agent with the given input content.
        
        Args:
            input_content: The input content to process
            metadata: Additional metadata for the request
            dry_run: Whether to run in dry run mode (no LLM calls)
            
        Returns:
            An AgentResponse object containing the agent's response
        """
        # Check if dry run is enabled
        if dry_run:
            logger.info(f"\033[1;3m{self._agent_name}\033[0m DRY RUN: Would have called LLM with: {input_content[:50]}...")
            return AgentResponse(
                content=f"[DRY RUN] {self._agent_name} would process: '{input_content}'"
            )
            
        # Run the Agno agent
        agno_response = self._agno_agent.run(input_content)
        
        # Extract tools used from the Agno response
        tools_used = []
        if hasattr(agno_response, 'tool_calls') and agno_response.tool_calls:
            tools_used = [
                {
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                    "result": tool_call.result
                }
                for tool_call in agno_response.tool_calls
            ]
        
        # Create response
        response = AgentResponse(
            content=agno_response.content
        )
        
        # Handle subscription message posting automatically
        if response.content and metadata and metadata.get("origin") == "subscription":
            logger.info(f"\033[1;3m{self._agent_name}\033[0m received subscription message, posting response")
            self.post_message(response.content)
            
        return response
    
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


class AgnoAgentAdapterWithInterest(AgnoAgentAdapter):
    """
    Agent adapter that checks for interest before processing messages.
    """
    
    def run(self, input_content: str, metadata: Dict[str, Any] = None, dry_run: bool = False) -> AgentResponse:
        """
        Run the agent with interest checking.
        
        This version checks if the agent is interested in the message before running.
        
        Args:
            input_content: The input content to process
            metadata: Additional metadata for the request
            dry_run: Whether to run in dry run mode (no LLM calls)
            
        Returns:
            An AgentResponse object containing the agent's response or None if not interested
        """
        # Check for "/stop" command
        if "/stop" in input_content:
            logger.info(f"\033[1;3m{self._agent_name}\033[0m received stop command")
            return AgentResponse(content=None)
        
        # Check for dry run mode first
        if dry_run:
            is_interested = check_agent_interest(input_content, self.agent_config)
            if is_interested:
                logger.info(f"\033[1;3m{self._agent_name}\033[0m DRY RUN: Would have responded (interested in message): {input_content[:50]}...")
                return AgentResponse(
                    content=f"[DRY RUN] {self._agent_name} would respond to message: '{input_content}'"
                )
            else:
                logger.info(f"\033[1;3m{self._agent_name}\033[0m DRY RUN: Not interested in message: {input_content[:50]}...")
                return AgentResponse(
                    content=None
                )
        
        # Check if the agent is interested in the message
        if check_agent_interest(input_content, self.agent_config):
            logger.info(f"\033[1;3m{self._agent_name}\033[0m is interested in message: {input_content[:50]}...")
            # Use the parent class run method
            return super().run(input_content, metadata, dry_run)
        else:
            logger.info(f"\033[1;3m{self._agent_name}\033[0m is not interested in message: {input_content[:50]}...")
            return AgentResponse(
                content=None
            )