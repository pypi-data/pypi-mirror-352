#!/usr/bin/env python3

"""
Agent registration and configuration management script.
This script handles the registration of agents with the AMP platform and manages their configurations.
"""

import os
import sys
import yaml
import argparse
import requests
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import inquirer
import datetime
import time
import logging

from amp_agent.amp_setup.auth_manager import get_auth_token, generate_api_key, AgentRegistrationError
from amp_agent.amp_setup.config_manager import ConfigManager
from amp_agent.amp_setup.platform_manager import PlatformManager
from amp_agent.amp_setup.auth_constants import API_BASE_URL

# Configure logging
logger = logging.getLogger(__name__)

def create_agent(config_manager: ConfigManager, agent_name: str, endpoint: str) -> Optional[str]:
    """Create a new agent on the platform."""
    try:
        auth_config = config_manager.auth_config
        platform_api_key = config_manager.get_platform_api_key()
        
        if not platform_api_key:
            logger.error("No valid platform API key available")
            raise AgentRegistrationError("No valid platform API key. Please complete the login process.")
        
        headers = {
            "Authorization": f"Basic {platform_api_key}",
            "Content-Type": "application/json"
        }

        
        payload = {
            "name": agent_name,
            "endpoint": endpoint,
            "role": "assistant",
            "organization_id": auth_config.organization_id,
            "platform_id": auth_config.platform_id,
            "endpoint_request_headers": [
                {
                    "Authorization": "Bearer <amp-token>"
                }
            ]
        }
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.post(f"{API_BASE_URL}/agents", headers=headers, json=payload, timeout=10)
                logger.info(f"Response: {response.json()}")
            except requests.exceptions.Timeout:
                retry_count += 1
                wait_time = 5 * retry_count
                logger.warning(f"Request timed out. Retry {retry_count}/{max_retries}")
                if retry_count >= max_retries:
                    return None
                time.sleep(wait_time)
                continue
            
            if response.status_code == 429:
                retry_count += 1
                retry_after = int(response.headers.get('Retry-After', 5 * retry_count))
                logger.warning(f"Rate limited. Retry {retry_count}/{max_retries}")
                time.sleep(retry_after)
                continue
            
            if response.status_code >= 400:
                error_msg = f"Error creating agent: {response.status_code} {response.text}"
                logger.error(error_msg)
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(2 ** retry_count)
                    continue
                else:
                    raise AgentRegistrationError(error_msg)
            
            try:
                result = response.json()
                agent_id = result.get("data", {}).get("id")
                
                if not agent_id:
                    logger.error(f"No agent ID in response: {result}")
                    raise AgentRegistrationError("No agent ID in response")
                
                logger.info(f"Created agent with ID: {agent_id}")
                return agent_id
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text}")
                raise AgentRegistrationError("Invalid JSON response")
            
    except Exception as e:
        logger.error(f"Unexpected error creating agent: {str(e)}", exc_info=True)
        return None

def select_agent(message: str, available_agents: List[Dict[str, Any]]) -> str:
    """Prompt user to select an agent from the available list."""
    choices = [
        (f"{agent['name']} ({agent['id']})", agent['id'])
        for agent in available_agents
    ]
    
    questions = [
        inquirer.List(
            'agent',
            message=message,
            choices=choices,
        ),
    ]
    
    answers = inquirer.prompt(questions)
    return answers['agent']

def validate_agent_ids(config_manager: ConfigManager, agent_config: Dict[str, Any], platform_agents: List[Dict[str, Any]], interactive: bool = True) -> bool:
    """Validate agent IDs and handle mismatches."""
    platform_agent_map = {agent['id']: agent for agent in platform_agents}
    
    for agent_id in agent_config["agents"].keys():
        stored_id = config_manager.get_agent_id(agent_id)
        
        if not stored_id:
            logger.info(f"Creating new agent: {agent_id}")
            try:
                new_id = create_agent(
                    config_manager,
                    agent_config["agents"][agent_id]["name"],
                    agent_config["agents"][agent_id]["url"]
                )
                if new_id is None:
                    logger.error(f"Failed to create agent {agent_id}")
                    continue
                
                config_manager.set_agent_id(agent_id, new_id)
                logger.info(f"Created new agent with ID: {new_id}")
            except AgentRegistrationError as e:
                logger.error(f"Error creating agent: {str(e)}")
                return False
        elif not platform_agents or stored_id not in platform_agent_map:
            if not platform_agents:
                logger.warning(f"No platform agents available. Trusting existing ID: {stored_id}")
            else:
                logger.info(f"\nAgent ID mismatch for {agent_id}")
                
                if interactive and platform_agents:
                    try:
                        name = agent_config['agents'][agent_id]['name']
                        selected_id = select_agent(f"Select an agent for {name}", platform_agents)
                        config_manager.set_agent_id(agent_id, selected_id)
                        logger.info(f"Updated {agent_id} with ID: {selected_id}")
                    except Exception as e:
                        logger.error(f"Error selecting agent: {str(e)}")
                        return False
                else:
                    logger.warning(f"Non-interactive mode: Creating new agent for {agent_id}")
                    try:
                        new_id = create_agent(
                            config_manager,
                            agent_config["agents"][agent_id]["name"],
                            agent_config["agents"][agent_id]["url"]
                        )
                        if new_id is None:
                            logger.error(f"Failed to create agent {agent_id}")
                            continue
                        
                        config_manager.set_agent_id(agent_id, new_id)
                        logger.info(f"Created new agent with ID: {new_id}")
                    except AgentRegistrationError as e:
                        logger.error(f"Error creating agent: {str(e)}")
                        return False
        else:
            logger.info(f"Agent {agent_id} exists with ID: {stored_id}")
    
    return True

def register_agent(config_manager: ConfigManager, agent_name: str, endpoint: str) -> Optional[str]:
    """Create a new agent on the platform."""
    try:
        auth_config = config_manager.auth_config
        platform_api_key = config_manager.get_platform_api_key()
        
        if not platform_api_key:
            logger.error("No valid platform API key available")
            raise AgentRegistrationError("No valid platform API key. Please complete the login process.")
        
        headers = {
            "Authorization": f"Basic {platform_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": agent_name,
            "endpoint": endpoint,
            "role": "assistant",
            "organization_id": auth_config.organization_id,
            "platform_id": auth_config.platform_id,
            "endpoint_request_headers": [
                {
                    "Authorization": "Bearer <amp-token>"
                }
            ]
        }
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.post(f"{API_BASE_URL}/agents", headers=headers, json=payload, timeout=10)
                logger.info(f"Response: {response.json()}")
            except requests.exceptions.Timeout:
                retry_count += 1
                wait_time = 5 * retry_count
                logger.warning(f"Request timed out. Retry {retry_count}/{max_retries}")
                if retry_count >= max_retries:
                    return None
                time.sleep(wait_time)
                continue
            
            if response.status_code == 429:
                retry_count += 1
                retry_after = int(response.headers.get('Retry-After', 5 * retry_count))
                logger.warning(f"Rate limited. Retry {retry_count}/{max_retries}")
                time.sleep(retry_after)
                continue
            
            if response.status_code >= 400:
                error_msg = f"Error creating agent: {response.status_code} {response.text}"
                logger.error(error_msg)
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(2 ** retry_count)
                    continue
                else:
                    raise AgentRegistrationError(error_msg)
            
            try:
                result = response.json()
                agent_id = result.get("data", {}).get("id")
                
                if not agent_id:
                    logger.error(f"No agent ID in response: {result}")
                    raise AgentRegistrationError("No agent ID in response")
                
                logger.info(f"Created agent with ID: {agent_id}")
                return agent_id
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text}")
                raise AgentRegistrationError("Invalid JSON response")
            
    except Exception as e:
        logger.error(f"Unexpected error creating agent: {str(e)}", exc_info=True)
        return None

def register_agents(config: Dict[str, Any] = None, interactive: bool = True, config_manager: Optional[ConfigManager] = None) -> bool:
    """
    Register multiple agents from configuration.
    
    Args:
        config: Optional agent configuration dictionary
        interactive: Whether to run in interactive mode
        config_manager: Optional ConfigManager instance. If not provided, a new one will be created.
        
    Returns:
        bool: True if all agents were registered successfully
    """
    try:
        if config_manager is None:
            config_manager = ConfigManager()
        platform_manager = PlatformManager()
        
        logger.info(f"Root directory: {config_manager.root_dir}")
        logger.info(f"Expected .env location: {config_manager.env_path}")
        
        # Load config if not provided
        if config is None:
            config = config_manager.load_agent_config()
        
        logger.info("Starting agent registration...")
        
        # Check authentication needs
        if config_manager.needs_authentication():
            if interactive:
                try:
                    # Get initial auth token
                    auth_data = get_auth_token()
                    logger.info("Got authentication token")
                    
                    # Generate and save API key
                    platform_details = generate_api_key(
                        auth_data['token'],
                        auth_data['organization_id'],
                        auth_data['platform_id']
                    )
                    
                    if platform_details:
                        # Save both auth data and platform details
                        auth_data.update(platform_details)
                        config_manager.save_auth_data(auth_data)
                        logger.info("Authentication and API key setup completed")
                        # Store API key and expiration in YAML for each agent
                        for agent_id in config["agents"].keys():
                            config_manager.set_agent_api_key(agent_id, platform_details["platform_api_key"])
                            config_manager.set_agent_api_key_expiration(agent_id, platform_details["platform_api_key_expires_at"])
                    else:
                        logger.error("Failed to generate API key")
                        return False
                        
                except Exception as e:
                    logger.error(f"Authentication failed: {str(e)}")
                    logger.warning("Continuing with existing credentials")
            else:
                logger.warning("Non-interactive mode: Skipping authentication")
        
        # Get platform agents with automatic caching and error handling
        logger.info("Getting platform agents...")
        api_key = config_manager.get_platform_api_key()
        logger.info(f"Using platform API key: {api_key[:10] if api_key else None}...")
        platform_agents = platform_manager.get_agents(api_key)
        
        # Validate agent IDs
        validation_result = validate_agent_ids(config_manager, config, platform_agents, interactive)
        if not validation_result:
            logger.error("Agent validation failed")
            return False
        
        logger.info("\nAll agents validated successfully!")
        logger.info("You can now start the agent service with:")
        logger.info("python main.py")
        return True
        
    except AgentRegistrationError as e:
        logger.error(f"Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    main() 