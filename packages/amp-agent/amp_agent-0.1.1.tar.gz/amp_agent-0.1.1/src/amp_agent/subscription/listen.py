import os
import uuid
import asyncio
import threading
import time
from typing import Optional, Dict, Any
from realtime import AsyncRealtimeClient, RealtimeSubscribeStates
from amp_agent.logging import subs_logger as logger


class SubscriptionManager:
    def __init__(self, core_config: Dict[str, Any], discovered_agents: Dict[str, Any]):
        self.core_config = core_config
        self.discovered_agents = discovered_agents
        self.realtime_client: Optional[AsyncRealtimeClient] = None
        self.channel = None
        self.loop = None
        self._is_setup = False
        self.message_callback = None
        self._should_stop = False

    async def setup(self, message_callback):
        """Set up the Supabase realtime subscription."""
        if self._is_setup:
            logger.info("Subscription already set up, skipping...")
            return

        if not message_callback:
            logger.error("No message callback provided")
            return

        self.message_callback = message_callback  # Store the callback
        try:
            # Initialize realtime client
            project_ref = self.core_config["supabase_url"].split("//")[1].split(".")[0]
            realtime_url = f"wss://{project_ref}.supabase.co/realtime/v1"
            self.realtime_client = AsyncRealtimeClient(realtime_url, self.core_config["supabase_anon_key"])
            logger.info("Successfully created realtime client")
            
            # Create channel
            self.channel = self.realtime_client.channel("subs_messages")
            
            def on_subscribe(status: RealtimeSubscribeStates, err: Exception = None):
                """Handle subscription status changes."""
                if status == RealtimeSubscribeStates.SUBSCRIBED:
                    logger.info("Successfully subscribed to realtime channel!")
                    self._is_setup = True
                elif status == RealtimeSubscribeStates.CHANNEL_ERROR:
                    logger.error(f"Error subscribing to channel: {err.args if err else 'Unknown error'}")
                elif status == RealtimeSubscribeStates.TIMED_OUT:
                    logger.error("Realtime server did not respond in time.")
                elif status == RealtimeSubscribeStates.CLOSED:
                    logger.error("Realtime channel was unexpectedly closed.")
                    self._is_setup = False
            
            # Set up postgres changes listener
            self.channel.on_postgres_changes(
                "INSERT",
                schema="public",
                table="subs_messages",
                callback=lambda payload: self.handle_message(payload)
            )
            
            # Subscribe
            await self.channel.subscribe(on_subscribe)
            logger.info("Successfully set up realtime subscription")
            
        except Exception as e:
            logger.error(f"Error setting up subscription: {e}", exc_info=True)
            self._is_setup = False

    def handle_message(self, payload):
        """Handle incoming messages for all agents."""
        try:
            if not self.message_callback:
                logger.error("No message callback available")
                return

            if 'data' not in payload or 'record' not in payload['data']:
                logger.warning("Invalid message format")
                return
            
            # Process the message for each agent
            for agent_id, agent_details in self.discovered_agents.items():
                try:
                    channel_id = payload['data']['record']['channel_id']
                    list_of_channels = agent_details["config"]["subscription_channels"]
                    logger.warning(f"listen: agent {agent_id} is registered to channel {channel_id}: {channel_id in list_of_channels}")
                    if(channel_id in list_of_channels):
                        # Run the callback in a separate task to prevent blocking
                        asyncio.create_task(self._run_callback(payload, agent_id, agent_details, "subs_messages"))
                except Exception as e:
                    logger.error(f"Error processing message for agent {agent_id}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    async def _run_callback(self, payload, agent_id, agent_details, channel_name):
        """Run the message callback in a separate task."""
        try:
            if not self.message_callback:
                logger.error("No message callback available")
                return

            # Ensure the callback is a coroutine
            if asyncio.iscoroutinefunction(self.message_callback):
                await self.message_callback(payload, agent_id, agent_details, channel_name)
            else:
                # If it's not a coroutine, just call it directly
                self.message_callback(payload, agent_id, agent_details, channel_name)
        except Exception as e:
            logger.error(f"Error in message callback for agent {agent_id}: {e}", exc_info=True)

    def run_forever(self, message_callback):
        """Run the subscription in a separate thread."""
        if not message_callback:
            logger.error("No message callback provided")
            return

        self.message_callback = message_callback  # Store the callback
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.setup(message_callback))
            while not self._should_stop:
                self.loop.run_forever()
                if not self._should_stop:
                    logger.warning("Subscription loop stopped unexpectedly, restarting...")
                    time.sleep(1)  # Wait a bit before restarting
        except Exception as e:
            logger.error(f"Error in subscription loop: {e}", exc_info=True)
        finally:
            if self.loop.is_running():
                self.loop.stop()
            self.loop.close()

    def start(self, message_callback):
        """Start the subscription in a separate thread."""
        if not hasattr(self, '_thread') or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run_forever, args=(message_callback,), daemon=True)
            self._thread.start()
            logger.info("Started subscription thread")

    def stop(self):
        """Stop the subscription."""
        self._should_stop = True
        if self.loop and self.loop.is_running():
            # Schedule cleanup in the event loop
            future = asyncio.run_coroutine_threadsafe(self.cleanup(), self.loop)
            try:
                # Wait for cleanup to complete with a timeout
                future.result(timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Cleanup timed out")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}", exc_info=True)
            finally:
                # Stop the event loop
                self.loop.call_soon_threadsafe(self.loop.stop)
        
        # Wait for the thread to finish
        if hasattr(self, '_thread') and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("Subscription thread did not stop gracefully")

    async def cleanup(self):
        """Clean up the subscription."""
        try:
            if self.channel:
                await self.channel.unsubscribe()
            if self.realtime_client:
                await self.realtime_client.remove_all_channels()
            self._is_setup = False
            logger.info("Removed all realtime channels")
        except Exception as e:
            logger.error(f"Error cleaning up subscription: {e}", exc_info=True)

# Create a singleton instance
_subscription_manager = None

def get_subscription_manager(core_config: Dict[str, Any], discovered_agents: Dict[str, Any]) -> 'SubscriptionManager':
    """Get or create the subscription manager instance."""
    global _subscription_manager
    if _subscription_manager is None:
        _subscription_manager = SubscriptionManager(core_config, discovered_agents)
    return _subscription_manager

def setup_subscription(core_config: Dict[str, Any], discovered_agents: Dict[str, Any], message_callback):
    """Set up the subscription using the subscription manager."""
    manager = get_subscription_manager(core_config, discovered_agents)
    manager.start(message_callback)

def cleanup_subscription():
    """Clean up the subscription using the subscription manager."""
    if _subscription_manager:
        _subscription_manager.stop()

