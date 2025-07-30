"""
Core server functionality for AMP agents.
This module provides the server setup and request handling for AMP agents.
"""
import json
import logging
import uuid
import time
import importlib
import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path
from flask import Flask, request, jsonify, g
from pydantic import ValidationError

from amp_agent.core.agent_interface import AgentInterface
from amp_agent.core.logging import logger
from amp_agent.core.auth import validate_token
from amp_agent.core.models import AgentMessage
from amp_agent.core.config import load_core_config

def run_async(coro):
    """
    Helper function to run coroutines in a sync context.
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def create_app(config_path: Optional[Path] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configured Flask application
    """
    # Import here to avoid circular dependency
    from amp_agent.amp_setup import ConfigManager
    
    server = AgentServer()
    server.initialize(config_path)
    return server.app

class AgentServer:
    """
    Unified server class that handles both agent management and HTTP server functionality.
    This class is responsible for:
    1. Agent discovery and initialization
    2. Configuration management
    3. HTTP request handling
    4. Server lifecycle management
    """
    
    def __init__(self):
        """Initialize the agent server with configuration management."""
        # Import here to avoid circular dependency
        from amp_agent.amp_setup import ConfigManager
        
        self.config_manager = ConfigManager()
        self.core_config = None
        self.discovered_agents = {}
        self.agent_config = None
        self.app = Flask(__name__)
        self._setup_routes()
        self._setup_error_handlers()

    def load_agent_factory(self, agent_id: str):
        """
        Load agent factory module.
        
        Args:
            agent_id: The identifier for the agent
            
        Returns:
            The agent factory function
        """
        try:
            # Get the module path from the config manager
            module_path = self.config_manager.get_agent_module_path(agent_id)
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the factory function - prefer get_factory() but fall back to create_agent for backwards compatibility
            if hasattr(module, 'get_factory'):
                return module.get_factory()
            elif hasattr(module, 'create_agent'):
                return module.create_agent
            
            raise ImportError(f"Could not find factory function in module {module_path}")
            
        except ImportError as e:
            logger.error(f"Failed to load factory for agent {agent_id}: {str(e)}", exc_info=True)
            raise

    def get_registered_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get dictionary of registered agents.
        
        Returns:
            Dictionary mapping agent IDs to their factory functions
        """
        agent_config = self.config_manager.load_agent_config()
        registered_agents = {}
        
        for agent_id in agent_config["agents"].keys():
            try:
                factory_func = self.load_agent_factory(agent_id)
                registered_agents[agent_id] = {
                    "factory_module": factory_func
                }
            except Exception as e:
                logger.error(f"Failed to register agent {agent_id}: {str(e)}", exc_info=True)
                continue
        
        return registered_agents

    def initialize_agents(self, registered_agents: Dict[str, Dict[str, Any]]):
        """
        Initialize all registered agents.
        
        Args:
            registered_agents: Dictionary of registered agent factories
            
        Returns:
            Dictionary of initialized agents with their configurations
        """
        agents = {}
        agent_configs = self.config_manager.load_agent_config()
        
        for agent_id, modules in registered_agents.items():
            try:
                # Get agent configuration
                agent_config = agent_configs["agents"][agent_id]
                
                # Configure interest model if present
                if agent_config.get("interest_model"):
                    interest_type = agent_config["interest_model"].get("type", "hybrid")
                    logger.info(f"Using {interest_type} interest model for {agent_id}")
                
                # Set agent ID
                agent_config["amp_agent_id"] = self.config_manager.get_agent_id(agent_id)
                
                # Register agent
                agents[agent_id] = {
                    "config": agent_config,
                    "factory_func": modules["factory_module"]
                }
                logger.info(f"Registered {agent_id} with ID: {agent_config['amp_agent_id']}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {agent_id}: {str(e)}", exc_info=True)
        
        return agents

    def initialize(self, config_path: Optional[Path] = None):
        """
        Initialize the server and all its components.
        
        Args:
            config_path: Optional path to configuration file
        """
        try:
            # Import here to avoid circular dependency
            from amp_agent.amp_setup import ConfigManager
            
            # Load configurations
            self.core_config = load_core_config()
            
            # Create new config manager with direct config path if provided
            if config_path:
                self.config_manager = ConfigManager(config_path=config_path)
            
            self.agent_config = self.config_manager.load_agent_config()
            
            # Initialize agents
            registered_agents = self.get_registered_agents()
            self.discovered_agents = self.initialize_agents(registered_agents)
            
            logger.info(f"Initialized {len(self.discovered_agents)} agents: {list(self.discovered_agents.keys())}")
            
        except Exception as e:
            logger.error("Failed to initialize server", exc_info=True)
            raise

    def _setup_routes(self):
        """Setup HTTP routes for the server."""
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint with detailed status."""
            try:
                if not self.discovered_agents:
                    return jsonify({
                        "status": "initializing",
                        "message": "Service is starting up"
                    }), 503
                
                return jsonify({
                    "status": "ok",
                    "version": "0.1.0",  # TODO: Get from package version
                    "agents": list(self.discovered_agents.keys()),
                    "timestamp": time.time()
                })
            except Exception as e:
                logger.error("Health check failed", exc_info=True)
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500

        @self.app.route("/api/v1/agents/<routing_id>/sessions/<session_id>", methods=["POST"])
        def handle_agent_request(routing_id: str, session_id: str):
            """Handle requests to specific agents."""
            logger.info(f"Handling agent request for {routing_id} with session {session_id}")
            # Check if agent exists
            if routing_id not in self.discovered_agents:
                logger.error(f"Agent not found: {routing_id}")
                return jsonify({"error": f"Agent '{routing_id}' not found"}), 404
            
            # Get agent details
            agent_details = self.discovered_agents[routing_id]
            logger.debug(f"Agent details: {agent_details}")
            try:
                # Validate authorization
                auth_header = request.headers.get("Authorization", "")
                if not auth_header.startswith("Bearer "):
                    logger.error("Invalid authorization header format")
                    return jsonify({"error": "Invalid authorization header"}), 401
                
                token = auth_header[7:]  # Remove "Bearer " prefix
                logger.debug(f"Token: {token}")
                # Validate token
                try:
                    expected_audience = f"amp:agent:{agent_details['config']['amp_agent_id']}"
                    logger.info(f"Validating token with expected audience: {expected_audience}")
                    
                    # Run async validation in sync context
                    claims = run_async(validate_token(
                        token=token,
                        jwks_url=self.core_config["jwks_url"],
                        audience=expected_audience
                    ))
                    
                    logger.debug(f"Token claims: {claims}")
                    logger.debug(f"Token claims aud: {claims.get('aud', 'not_found')}")
                except ValueError as e:
                    logger.error(f"Token validation error: {str(e)}", exc_info=True)
                    return jsonify({"error": "Authentication failed", "message": str(e)}), 401
                
                # Get user ID from token
                user_id = claims["sub"]
                logger.debug(f"Request authenticated for user: {user_id}")
                
                # Parse and validate request body
                try:
                    request_data = request.get_json()
                    message = AgentMessage.parse_obj(request_data)
                except ValidationError as e:
                    logger.error(f"Invalid request data: {str(e)}")
                    return jsonify({"error": "Invalid request data", "details": str(e)}), 400
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in request: {str(e)}")
                    return jsonify({"error": "Invalid JSON in request"}), 400
                
                # Create agent instance
                logger.debug(f"Creating agent instance for session_id={session_id}, user_id={user_id}")
                logger.info(f"Processing message: {message}")
                try:
                    agent = agent_details["factory_func"](
                        agent_config=agent_details["config"],
                        core_config=self.core_config,
                        session_id=session_id,
                        user_id=user_id
                    )
                except Exception as agent_error:
                    logger.error(f"Failed to create agent instance: {str(agent_error)}", exc_info=True)
                    # Log all available context that might help debug the issue
                    logger.error(f"Agent config: {agent_details['config']}")
                    logger.error(f"Core config: {self.core_config}")
                    raise
                
                # Extract content and process message
                input_content = message.last_content
                if input_content is None:
                    logger.error("Received message list is empty")
                    return jsonify({"error": "Invalid request data", "details": "Message list cannot be empty"}), 400

                metadata = message.metadata if hasattr(message, 'metadata') and message.metadata is not None else {}
                metadata['origin'] = "dynamic_route"
                response = agent.run(input_content, metadata=metadata)
                
                # Construct response
                response_message = {}
                if response.content is not None:
                    response_message["content"] = response.content
                if response.metadata is not None:
                    response_message["metadata"] = response.metadata

                response_payload = {
                    "message": response_message,
                }
                
                logger.info(f"Sending response payload: {response_payload}")
                return jsonify(response_payload)
                
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}", exc_info=True)
                # Add more context to the error response
                error_details = {
                    "error": "Internal server error",
                    "message": str(e),
                    "type": e.__class__.__name__,
                    "agent_id": routing_id,
                    "session_id": session_id
                }
                return jsonify(error_details), 500

    def _setup_error_handlers(self):
        """Setup error handlers for the server."""
        
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({"error": "Bad request", "message": str(error)}), 400

        @self.app.errorhandler(401)
        def unauthorized(error):
            return jsonify({"error": "Unauthorized", "message": str(error)}), 401

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Not found", "message": str(error)}), 404

        @self.app.errorhandler(500)
        def server_error(error):
            return jsonify({"error": "Server error", "message": str(error)}), 500

    def run(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        """Run the server."""
        self.app.run(host=host, port=port, debug=debug)

    def wsgi_app(self, environ, start_response):
        """WSGI application entry point."""
        with self.app.request_context(environ):
            g.execution_id = str(uuid.uuid4())
            g.start_time = time.time()
            response = self.app.full_dispatch_request()
            duration = time.time() - g.start_time
            logger.info(f"Request completed in {duration:.3f}s")
            return response(environ, start_response) 