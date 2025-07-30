"""
Platform agent management and caching.
"""

import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from amp_agent.amp_setup.auth_constants import API_BASE_URL

# Configure logging
logger = logging.getLogger(__name__)

class PlatformManager:
    """
    Manages platform agent fetching and caching.
    
    Features:
    - Automatic caching with configurable TTL
    - Rate limiting
    - Retry mechanism with exponential backoff
    - Error handling with fallback to cache
    """
    
    def __init__(self, cache_ttl: int = 300, rate_limit: float = 1.0):
        """
        Initialize the platform agent manager.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
            rate_limit: Minimum time between API calls in seconds (default: 1 second)
        """
        self._cache = {}
        self._cache_ttl = cache_ttl
        self._rate_limit = rate_limit
        self._last_api_call = 0

    def _should_use_cache(self, cache_key: str) -> bool:
        """Check if cache should be used."""
        if cache_key not in self._cache:
            return False
            
        cache_entry = self._cache[cache_key]
        return time.time() - cache_entry['timestamp'] < self._cache_ttl

    def _apply_rate_limit(self):
        """Apply rate limiting if needed."""
        elapsed = time.time() - self._last_api_call
        if elapsed < self._rate_limit:
            time.sleep(self._rate_limit - elapsed)

    def _make_request(self, url: str, headers: Dict[str, str], params: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry mechanism."""
        retry_count = 0
        while retry_count < max_retries:
            try:
                self._apply_rate_limit()
                response = requests.get(url, headers=headers, params=params, timeout=10)
                self._last_api_call = time.time()

                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    time.sleep(retry_after)
                    retry_count += 1
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count >= max_retries:
                    return None
                time.sleep(5 * retry_count)  # Exponential backoff
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                return None

        return None

    def get_agents(self, api_key: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get platform agents with caching and error handling.
        
        Args:
            api_key: Platform API key
            force_refresh: Whether to force a cache refresh
            
        Returns:
            List of agent dictionaries
        """
        if not api_key:
            logger.error("No API key provided")
            return []

        cache_key = f"agents_{api_key[:10]}"
        
        # Return cached data if valid and not forcing refresh
        if not force_refresh and self._should_use_cache(cache_key):
            logger.debug("Using cached platform agents")
            return self._cache[cache_key]['data']

        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json"
        }

        all_agents = []
        current_page = 1

        while True:
            params = {
                "page": current_page,
                "per_page": 100,
                "direction": "desc",
                "order_by": "created_at"
            }

            response_data = self._make_request(f"{API_BASE_URL}/agents", headers, params)
            
            if not response_data:
                # If request failed and we have cached data, use it
                if cache_key in self._cache:
                    logger.warning("Request failed, using cached data")
                    return self._cache[cache_key]['data']
                return []

            all_agents.extend(response_data["data"])
            
            # Check for more pages
            pagination = response_data.get("meta", {}).get("pagination", {})
            if not pagination or current_page >= pagination.get("total_pages", 1):
                break
                
            current_page += 1

        # Update cache
        self._cache[cache_key] = {
            'data': all_agents,
            'timestamp': time.time()
        }

        return all_agents

    def clear_cache(self):
        """Clear the agent cache."""
        self._cache = {} 