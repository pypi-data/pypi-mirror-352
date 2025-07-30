import os
import asyncio
import websockets
import json
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from amp_agent.logging import subs_logger as logger

class AMPWebSocketManager:
    def __init__(self, core_config: Dict[str, Any], discovered_agents: Dict[str, Any], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        self.core_config = core_config
        self.discovered_agents = discovered_agents
        self.websocket = None
        self.loop = None
        self._is_setup = False
        self.message_callback = None
        self._should_stop = False
        self._thread = None
        # Ensure dates are in UTC
        self.start_date = self._ensure_utc(start_date) if start_date else None
        self.end_date = self._ensure_utc(end_date) if end_date else None
        self._reconnect_delay = 1  # Initial delay in seconds
        self._max_reconnect_delay = 60  # Maximum delay in seconds
        self._current_token = None
        self._current_channel_ids = None
        
        logger.info(f"Initialized WebSocket manager with UTC filters - Start: {self.start_date}, End: {self.end_date}")

    def _ensure_utc(self, dt: Optional[datetime]) -> Optional[datetime]:
        """Ensure a datetime is in UTC."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            # If no timezone is set, assume UTC
            return dt.replace(tzinfo=timezone.utc)
        if dt.tzinfo != timezone.utc:
            # If timezone is set but not UTC, convert to UTC
            return dt.astimezone(timezone.utc)
        return dt

    async def setup(self, user_a2c_token: str, channel_ids: list[str], message_callback):
        """Set up the AMP WebSocket connection."""
        if not message_callback:
            logger.error("No message callback provided")
            return

        self.message_callback = message_callback
        self._current_token = user_a2c_token
        self._current_channel_ids = channel_ids

        while not self._should_stop:
            try:
                if self._is_setup:
                    logger.info("WebSocket already set up, attempting to reconnect...")
                    await asyncio.sleep(self._reconnect_delay)
                    # Implement exponential backoff
                    self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)
                else:
                    self._reconnect_delay = 1  # Reset delay on successful connection

                uri = f"wss://api.dev.theswarmhub.com/api/v1/ws?token={self._current_token}&channel_id={self._current_channel_ids[0]}"
                logger.info(f"Connecting to WebSocket... {uri[:50]}...")
                
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    self._is_setup = True
                    logger.info(f"Connected to WebSocket - {self._current_channel_ids}")
                    
                    while not self._should_stop:
                        try:
                            message = await websocket.recv()
                            await self.handle_message(message)
                        except websockets.exceptions.ConnectionClosed as e:
                            logger.error("WebSocket connection closed", exc_info=True)
                            self._is_setup = False
                            break
                        except Exception as e:
                            logger.error(f"Error receiving message: {e}", exc_info=True)
                            if "connection" in str(e).lower():
                                self._is_setup = False
                                break

            except Exception as e:
                logger.error(f"Error setting up WebSocket: {e}", exc_info=True)
                self._is_setup = False
                await asyncio.sleep(self._reconnect_delay)
                continue

            if not self._should_stop:
                logger.info(f"Connection lost. Reconnecting in {self._reconnect_delay} seconds...")
                await asyncio.sleep(self._reconnect_delay)

    def run_forever(self, user_a2c_token: str, channel_ids: list[str], message_callback):
        """Run the WebSocket connection in a separate thread."""
        if not message_callback:
            logger.error("No message callback provided")
            return

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.setup(user_a2c_token, channel_ids, message_callback))
        except Exception as e:
            logger.error(f"Error in WebSocket loop: {e}", exc_info=True)
        finally:
            if self.loop.is_running():
                self.loop.stop()
            self.loop.close()

    def start(self, user_a2c_token: str, channel_ids: list[str], message_callback):
        """Start the WebSocket connection in a separate thread."""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(
                target=self.run_forever,
                args=(user_a2c_token, channel_ids, message_callback),
                daemon=True
            )
            self._thread.start()
            logger.info("Started WebSocket thread")

    def _filter_message_by_date(self, message_payload: Dict) -> bool:
        """
        Filter a message based on its sent_at timestamp.
        
        Args:
            message_payload: The message payload containing sent_at field
            
        Returns:
            bool: True if message should be processed, False if it should be filtered out
        """
        if "sent_at" not in message_payload:
            return True  # No date filtering if sent_at is not present
            
        try:
            # Parse the UTC timestamp from the message
            # The format '2025-05-08T08:01:02Z' indicates this is already in UTC
            sent_at = message_payload["sent_at"]
            message_date = datetime.strptime(sent_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            
            # Convert filter dates to UTC if they aren't already
            start_date = self._ensure_utc(self.start_date) if self.start_date else None
            end_date = self._ensure_utc(self.end_date) if self.end_date else None
            
            # Log all dates in ISO format for clarity
            logger.debug(
                "Comparing dates (all UTC) - Message: %s, Start: %s, End: %s",
                message_date.isoformat(),
                start_date.isoformat() if start_date else None,
                end_date.isoformat() if end_date else None
            )
            
            # Skip if message is outside the date range
            if start_date and message_date < start_date:
                logger.debug(
                    "Message too old - Message time (UTC): %s is before start time (UTC): %s", 
                    message_date.isoformat(), 
                    start_date.isoformat()
                )
                return False
                
            if end_date and message_date > end_date:
                logger.info(
                    "Message too new - Message time (UTC): %s is after end time (UTC): %s", 
                    message_date.isoformat(), 
                    end_date.isoformat()
                )
                return False
            
            logger.debug("Message within time range - Processing message from: %s", message_date.isoformat())
            return True
            
        except ValueError as e:
            logger.error("Error parsing message date: %s - %s", 
                       message_payload["sent_at"], str(e))
            return False

    async def handle_message(self, message: str):
        """Handle incoming WebSocket messages."""
        try:
            if not self.message_callback:
                logger.error("No message callback available")
                return

            try:
                parsed_message = json.loads(message)
                
                # Only process message type events
                if "type" not in parsed_message or parsed_message["type"] != "message":
                    return

                # Apply date filtering before processing agents
                if not self._filter_message_by_date(parsed_message["payload"]):
                    logger.debug(f"Skipping message due to date filtering: {parsed_message['payload']['sent_at']}")
                    return
                
                # Process message for each agent only if it passed date filtering
                for agent_id, agent_details in self.discovered_agents.items():
                    try:
                        channel_id = parsed_message["payload"]["channel_id"]
                        list_of_channels = agent_details["config"]["subscription_channels"]
                        logger.debug(f"\033[1;3m{agent_id}\033[0m Processing message in channel {channel_id}, subscribed channels: {list_of_channels}")
                        
                        if channel_id in list_of_channels:
                            logger.info(f"\033[1;3m{agent_id}\033[0m Calling callback for message in channel {channel_id}")
                            await self._run_callback(parsed_message, agent_id, agent_details)
                        else:
                            logger.info(f"\033[1;3m{agent_id}\033[0m Channel {channel_id} not in agent's subscription list: {list_of_channels}")
                                
                    except Exception as e:
                        logger.error(f"Error processing message for agent {agent_id}: {e}", exc_info=True)
                        
            except json.JSONDecodeError:
                logger.error("Received invalid JSON message")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    async def _run_callback(self, payload, agent_id, agent_details):
        """Run the message callback for an agent."""
        try:
            if not self.message_callback:
                logger.error("No message callback available")
                return

            if asyncio.iscoroutinefunction(self.message_callback):
                await self.message_callback(payload, agent_id, agent_details)
            else:
                self.message_callback(payload, agent_id, agent_details)
        except Exception as e:
            logger.error(f"Error in message callback for agent {agent_id}: {e}", exc_info=True)

    def stop(self):
        """Stop the WebSocket connection."""
        self._should_stop = True
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.cleanup_sync)
        
        if hasattr(self, '_thread') and self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("WebSocket thread did not stop gracefully")

    def cleanup_sync(self):
        """Synchronous cleanup for the WebSocket connection."""
        try:
            if self.websocket:
                self.loop.run_until_complete(self.websocket.close())
            self._is_setup = False
            logger.info("Closed WebSocket connection")
        except Exception as e:
            logger.error(f"Error cleaning up WebSocket: {e}", exc_info=True)

# Create a singleton instance
_websocket_manager = None

def get_websocket_manager(
    core_config: Dict[str, Any], 
    discovered_agents: Dict[str, Any],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> 'AMPWebSocketManager':
    """Get or create the WebSocket manager instance."""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = AMPWebSocketManager(core_config, discovered_agents, start_date, end_date)
    return _websocket_manager

def setup_amp_websocket(
    core_config: Dict[str, Any],
    discovered_agents: Dict[str, Any],
    user_a2c_token: str,
    channel_ids: list[str],
    message_callback,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Set up the WebSocket connection using the WebSocket manager."""
    manager = get_websocket_manager(core_config, discovered_agents, start_date, end_date)
    manager.start(user_a2c_token, channel_ids, message_callback)

def cleanup_amp_websocket():
    """Clean up the WebSocket connection using the WebSocket manager."""
    if _websocket_manager:
        _websocket_manager.stop()
