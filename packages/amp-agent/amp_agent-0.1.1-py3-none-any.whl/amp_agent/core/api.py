import requests
import logging
from typing import Dict, Any, List, Optional, Tuple
import os
import json

# Configure logging
logger = logging.getLogger(__name__)

API_URL = "https://api.dev.theswarmhub.com"

def _make_request(
    method: str,
    endpoint: str,
    headers: Dict[str, str],
    data: Optional[Dict] = None,
    expected_status: int = 200
) -> Tuple[bool, Dict[str, Any]]:
    """
    Make an HTTP request to the API with consistent logging.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        headers: Request headers
        data: Request payload
        expected_status: Expected HTTP status code
        
    Returns:
        Tuple of (success: bool, response_data: Dict)
    """
    url = f"{API_URL}{endpoint}"
    
    # Log request details
    logger.debug(
        "Making API request - Method: %s, URL: %s, Headers: %s, Payload: %s",
        method,
        url,
        {k: v for k, v in headers.items() if k.lower() != 'authorization'},  # Don't log auth tokens
        json.dumps(data, indent=2) if data else None
    )
    
    try:
        response = requests.request(method, url, headers=headers, json=data)
        status_code = response.status_code
        
        # Try to parse response as JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}
        
        # Log response details
        logger.debug(
            f"API response received - Status: {status_code}, Response: {json.dumps(response_data, indent=2)}"
        )
        
        if status_code == expected_status:
            logger.debug(
                f"API request successful - Method: {method}, Endpoint: {endpoint}, Status: {status_code}"
            )
            return True, response_data
        else:
            logger.error(
                f"API request failed - Method: {method}, Endpoint: {endpoint}, Expected Status: {expected_status}, Got Status: {status_code}, Headers: {headers}, Response: {response_data}",
                exc_info=True
            )
            return False, response_data
            
    except requests.exceptions.RequestException as e:
        logger.error(
            f"API request error - Method: {method}, Endpoint: {endpoint}, Error: {str(e)}",
            exc_info=True
        )
        return False, {"error": str(e)}

def get_api_key() -> str:
    """Get the SwarmHub platform API key from environment variables."""
    api_key = os.getenv("SWARMHUB_PLATFORM_API_KEY")
    if not api_key:
        logger.error("SWARMHUB_PLATFORM_API_KEY environment variable not set")
    return api_key

def send_messages(
    a2c_token: str, 
    channel_id: str,
    message: Dict[str, Any],
    mentions: List[str] = []
) -> Dict[str, Any]:
    """
    Send a message to a channel.
    
    Args:
        a2c_token: Agent-to-channel token
        channel_id: Target channel ID
        message: Message content
        mentions: List of agent IDs to mention
        
    Returns:
        API response data
    """
    headers = {
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {a2c_token}"
    }
    
    payload = {
        "channel_id": channel_id,
        "message": message,
        "mentions": mentions
    }
    
    success, response = _make_request(
        method="POST",
        endpoint="/api/v1/messages",
        headers=headers,
        data=payload
    )
    
    return response

def create_a2c_token(agent_id: str, channel_id: str, basic_token: str) -> Optional[str]:
    """
    Create an agent-to-channel token.
    
    Args:
        agent_id: The agent's ID
        channel_id: The channel ID
        basic_token: Basic authentication token
        
    Returns:
        The A2C token if successful, None otherwise
    """
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "agent_id": agent_id,
        "channel_id": channel_id
    }
    
    success, response = _make_request(
        method="POST",
        endpoint="/api/v1/tokens/a2c",
        headers=headers,
        data=payload,
        expected_status=200
    )
    
    if success and 'data' in response and 'token' in response['data']:
        return response['data']['token']
    return None

def create_channels(
    basic_token: str,
    agent_id: Optional[str] = None,
    message_visibility: str = "all",
    http_callback_enabled: bool = False
) -> Optional[str]:
    """
    Create a new channel.
    
    Args:
        basic_token: Basic authentication token
        agent_id: Optional owner agent ID
        message_visibility: Message visibility setting
        http_callback_enabled: Whether HTTP callbacks are enabled
        
    Returns:
        Channel ID if successful, None otherwise
    """
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "owner_agent_id": agent_id,
        "config": {
            "message_visibility": message_visibility,
            "http_callback_enabled": http_callback_enabled
        }
    }
    
    success, response = _make_request(
        method="POST",
        endpoint="/api/v1/channels",
        headers=headers,
        data=payload,
        expected_status=201
    )
    
    if success and 'data' in response and 'id' in response['data']:
        channel_id = response['data']['id']
        if(agent_id):
            payload = {"agent_id": agent_id}
            success, response = _make_request(
                method="POST",
                endpoint=f"/api/v1/channels/{channel_id}/agents",
                headers=headers,
                data=payload,
                expected_status=200
            )
        return channel_id
    return None

def list_channels(basic_token: str) -> Dict[str, Any]:
    """
    List all available channels.
    
    Args:
        basic_token: Basic authentication token
        
    Returns:
        API response data
    """
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/json"
    }
    
    success, response = _make_request(
        method="GET",
        endpoint="/api/v1/channels",
        headers=headers
    )
    
    return response

def list_channel_agents(basic_token: str, channel_id: str) -> Dict[str, Any]:
    """
    List all available channels.
    
    Args:
        basic_token: Basic authentication token
        
    Returns:
        API response data
    """
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/json"
    }
    
    success, response = _make_request(
        method="GET",
        endpoint=f"/api/v1/channels/{channel_id}/agents",
        headers=headers
    )
    # Extract just the agent_ids from the response
    if success and response.get('data'):
        return [agent['agent_id'] for agent in response['data']]
    return response

    