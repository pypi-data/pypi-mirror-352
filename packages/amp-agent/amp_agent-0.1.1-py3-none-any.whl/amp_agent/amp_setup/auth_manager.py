#!/usr/bin/env python3

"""
Authentication manager for AMP platform.
Handles user authentication and token management.
"""

import os
import sys
import webbrowser
import json
import time
import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv, set_key
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import logging
import secrets
import urllib.parse
import socket
from amp_agent.amp_setup.auth_constants import (
    AUTH_ENV_MAPPING,
    ENV_AUTH_MAPPING,
    REQUIRED_AUTH_KEYS,
    API_BASE_URL,
    PORTAL_URL,
    CALLBACK_PORT,
    CALLBACK_URL
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# pwd J6wGaKtEXBXsVirtoF7j 

class AgentRegistrationError(Exception):
    """Custom exception for agent registration errors."""
    pass

def generate_api_key(access_token: str, organization_id: str, platform_id: str) -> Optional[Dict[str, str]]:
    """
    Generate an API key for the organization and platform.
    
    Args:
        access_token: Authentication token
        organization_id: Organization ID
        platform_id: Platform ID
        
    Returns:
        Dictionary containing platform details if successful, None otherwise
    """
    try:
        expires_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=90)).isoformat()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "name": "Onboarding API Key", 
            "expires_at": expires_at
        }
        url = f"{API_BASE_URL}/admin/organizations/{organization_id}/platforms/{platform_id}/api-keys"
        
        logger.info("Generating API key...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        platform_details = {
            "platform_client_id": result.get("client_id"),
            "platform_client_secret": result.get("client_secret"),
            "platform_api_key": result.get("client_auth"),
            "platform_api_key_expires_at": result.get("expires_at")
        }

        if not all(platform_details.values()):
            logger.error(f"Incomplete API key response: {platform_details}")
            raise "Incomplete API key response"
        
        logger.info("API key generated successfully")
        return platform_details
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to generate API key: {str(e)}", exc_info=True)
        return None

def get_auth_token() -> Optional[str]:
    """Get authentication token, triggering login if needed"""
    # Load environment variables
    load_dotenv()
    
    # Clear existing token before starting new flow
    clear_auth_token()
    
    # Always start a new login flow
    logger.info("Starting new login flow...")
    
    # Create events to signal when we receive the required data
    auth_completed = threading.Event()
    auth_data = {
        'token': None,
        'organization_id': None,
        'platform_id': None
    }
    
    class TokenCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/callback'):
                query = self.path.split('?')[1] if '?' in self.path else ''
                params = dict(param.split('=') for param in query.split('&')) if query else {}
                
                # Check if we have all required parameters
                required_params = ['token', 'organization_id', 'platform_id']
                if all(key in params for key in required_params):
                    # Store values in environment
                    env_path = Path(__file__).parent.parent / ".env"
                    
                    # Store all values
                    auth_data['token'] = params['token']
                    auth_data['organization_id'] = params['organization_id']
                    auth_data['platform_id'] = params['platform_id']
                    
                    # Use AUTH_ENV_MAPPING to save values
                    for auth_key in required_params:
                        if auth_key in params:
                            set_key(env_path, AUTH_ENV_MAPPING[auth_key], params[auth_key])
                    
                    # Send success response with styled HTML
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                    self.send_header('Pragma', 'no-cache')
                    self.end_headers()
                    
                    success_html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Authentication Successful</title>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {
                                margin: 0;
                                padding: 0;
                                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                                background: linear-gradient(to bottom right, #030507, #0c1015);
                                min-height: 100vh;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                            }
                            .container {
                                width: 100%;
                                max-width: 28rem;
                                padding: 2rem;
                                background: rgba(10,15,25,0.95);
                                border: 1px solid rgba(157,92,255,0.2);
                                border-radius: 1rem;
                                text-align: center;
                                position: relative;
                                z-index: 1;
                            }
                            .glow {
                                position: absolute;
                                width: 50%;
                                height: 50%;
                                border-radius: 50%;
                                pointer-events: none;
                            }
                            .glow-1 {
                                top: 25%;
                                left: 25%;
                                background: #9d5cff;
                                opacity: 0.07;
                                filter: blur(120px);
                            }
                            .glow-2 {
                                bottom: 25%;
                                right: 25%;
                                background: #ff2ee6;
                                opacity: 0.05;
                                filter: blur(120px);
                            }
                            h1 {
                                font-size: 1.5rem;
                                font-weight: 500;
                                background: linear-gradient(to right, #9d5cff, #ff2ee6);
                                -webkit-background-clip: text;
                                -webkit-text-fill-color: transparent;
                                margin-bottom: 1rem;
                            }
                            p {
                                color: #9ca3af;
                                margin-bottom: 1.5rem;
                            }
                            .checkmark {
                                width: 4rem;
                                height: 4rem;
                                margin: 0 auto;
                                color: #9d5cff;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="glow glow-1"></div>
                        <div class="glow glow-2"></div>
                        <div class="container">
                            <h1>Authentication Successful!</h1>
                            <p>Your agent registration is complete. You can now close this window and return to the terminal.</p>
                            <svg class="checkmark" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(success_html.encode())
                    
                    # Signal that we received all required data
                    auth_completed.set()
                else:
                    missing = [key for key in ['token', 'organization_id', 'platform_id'] if key not in params]
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f"Authentication failed: Missing required parameters: {', '.join(missing)}".encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    server = None
    try:
        # Try to create the server with SO_REUSEADDR option
        server = HTTPServer(('localhost', CALLBACK_PORT), TokenCallbackHandler)
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Construct login URL with callback parameters
        callback_params = {
            'source': 'register_agents',
            'callback': CALLBACK_URL,
            '_cb': str(int(time.time()))  # Add cache busting parameter
        }
        login_url = f"{PORTAL_URL}?{urllib.parse.urlencode(callback_params)}"
        
        # Open browser for login
        webbrowser.open(login_url)
        
        # Wait for all required data with timeout
        logger.info("Waiting for authentication and organization/platform selection...")
        if not auth_completed.wait(timeout=300):  # 5 minute timeout
            raise Exception("Authentication timed out waiting for all required data")
        
        return auth_data
        
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        return None
    finally:
        if server:
            try:
                server.shutdown()
                server.server_close()
            except Exception as e:
                logger.error(f"Error shutting down server: {str(e)}")

def clear_auth_token():
    """Clear all authentication-related environment variables"""
    env_path = Path(__file__).parent.parent / ".env"
    
    # Clear all auth-related environment variables
    for env_key in AUTH_ENV_MAPPING.values():
        set_key(env_path, env_key, "")
    
    # Force reload of environment variables
    load_dotenv(override=True)



if __name__ == "__main__":
    # Test authentication
    token = get_auth_token()
    if token:
        print("Authentication successful!")
    else:
        print("Authentication failed!") 