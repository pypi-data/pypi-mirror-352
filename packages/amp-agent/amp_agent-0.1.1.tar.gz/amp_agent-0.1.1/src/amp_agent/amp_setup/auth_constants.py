"""
Shared authentication constants and mappings.
"""
import os
# Mapping between auth_data keys and environment variable names
AUTH_ENV_MAPPING = {
    'token': 'SWARMHUB_AUTH_TOKEN',
    'organization_id': 'SWARMHUB_ORGANIZATION_ID',
    'platform_id': 'SWARMHUB_PLATFORM_ID',
    'platform_client_id': 'SWARMHUB_PLATFORM_CLIENT_ID',
    'platform_client_secret': 'SWARMHUB_PLATFORM_CLIENT_SECRET',
    'platform_api_key': 'SWARMHUB_PLATFORM_API_KEY',
    'platform_api_key_expires_at': 'SWARMHUB_PLATFORM_API_KEY_EXPIRES_AT'
}

# Inverse mapping for convenience
ENV_AUTH_MAPPING = {env_key: auth_key for auth_key, env_key in AUTH_ENV_MAPPING.items()}

# Required keys for authentication
REQUIRED_AUTH_KEYS = ['token', 'organization_id', 'platform_id', 'platform_api_key']

# API endpoints
API_BASE_URL = "https://api.dev.theswarmhub.com/api/v1"
PORTAL_URL = os.getenv('SWARMHUB_PORTAL_URL', "https://portal.dev.theswarmhub.com/application-login")

# Callback configuration
CALLBACK_PORT = 8081
CALLBACK_URL = f"http://localhost:{CALLBACK_PORT}/callback" 