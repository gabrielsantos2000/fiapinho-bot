"""
Webhook Manager for Fiapinho Bot

This module manages different webhook types and routes them to appropriate handlers.
Currently, supports calendar synchronization with FIAP platform.
"""

import os
import logging
from typing import Dict, Any, Optional
import discord

logger = logging.getLogger(__name__)


class WebhookManager:
    """
    Main webhook manager that coordinates different webhook types.
    """

    def __init__(self, bot):
        """
        Initialize webhook manager.

        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self.webhooks = {}
        self._initialize_webhooks()

    def _initialize_webhooks(self):
        """Initialize all webhook handlers."""
        try:
            # Lazy import to avoid circular imports
            from .sync_calendar.app import CalendarSyncWebhook
            # Initialize calendar sync webhook
            self.webhooks['sync_calendar'] = CalendarSyncWebhook(self.bot)
            logger.info("Webhook manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing webhook manager: {e}")

    async def sync_calendar(self, resync: bool = False) -> bool:
        """
        Execute calendar synchronization webhook.

        Returns:
            bool: True if sync was successful, False otherwise
        """
        try:
            if 'sync_calendar' not in self.webhooks:
                logger.error("Calendar sync webhook not initialized")
                return False

            webhook = self.webhooks['sync_calendar']
            return await webhook.execute(resync=resync)

        except Exception as e:
            logger.error(f"Error executing calendar sync: {e}")
            return False

    async def execute_webhook(self, webhook_type: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific webhook type.

        Args:
            webhook_type: Type of webhook to execute
            **kwargs: Additional parameters for the webhook

        Returns:
            Dict[str, Any]: Result of webhook execution
        """
        if webhook_type not in self.webhooks:
            logger.error(f"Unknown webhook type: {webhook_type}")
            return {
                'success': False,
                'error': f'Unknown webhook type: {webhook_type}'
            }

        try:
            webhook = self.webhooks[webhook_type]

            if webhook_type == 'sync_calendar':
                success = await webhook.execute(**kwargs)
                return {
                    'success': success,
                    'webhook_type': webhook_type
                }

            logger.warning(f"No execution method defined for webhook type: {webhook_type}")
            return {
                'success': False,
                'error': f'No execution method for webhook type: {webhook_type}'
            }

        except Exception as e:
            logger.error(f"Error executing webhook {webhook_type}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_webhook_status(self, webhook_type: str = None) -> Dict[str, Any]:
        """
        Get status information about webhooks.

        Args:
            webhook_type: Specific webhook type to check (optional)

        Returns:
            Dict[str, Any]: Status information
        """
        try:
            if webhook_type:
                if webhook_type not in self.webhooks:
                    return {
                        'error': f'Unknown webhook type: {webhook_type}'
                    }

                webhook = self.webhooks[webhook_type]
                return {
                    'webhook_type': webhook_type,
                    'initialized': True,
                    'last_execution': getattr(webhook, 'last_execution', None)
                }

            # Return status for all webhooks
            status = {}
            for name, webhook in self.webhooks.items():
                status[name] = {
                    'initialized': True,
                    'last_execution': getattr(webhook, 'last_execution', None)
                }

            return status

        except Exception as e:
            logger.error(f"Error getting webhook status: {e}")
            return {
                'error': str(e)
            }

    async def send_notification(self, message: str, embed: Optional[discord.Embed] = None,
                                channel_id: str = None) -> bool:
        """
        Send notification to Discord channel.

        Args:
            message: Text message to send
            embed: Optional Discord embed
            channel_id: Specific channel ID (optional, uses default from env)

        Returns:
            bool: True if message was sent successfully
        """
        try:
            if not channel_id:
                channel_id = os.getenv('DISCORD_CALENDAR_CHANNEL_ID')

            if not channel_id:
                logger.error("No Discord channel ID configured")
                return False

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Could not find Discord channel: {channel_id}")
                return False

            if embed:
                await channel.send(message, embed=embed)
            else:
                await channel.send(message)

            logger.info("Notification sent successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    async def shutdown(self):
        """Clean shutdown of webhook manager."""
        try:
            logger.info("Shutting down webhook manager...")

            # Shutdown individual webhooks
            for name, webhook in self.webhooks.items():
                if hasattr(webhook, 'shutdown'):
                    await webhook.shutdown()

            logger.info("Webhook manager shutdown complete")

        except Exception as e:
            logger.error(f"Error during webhook manager shutdown: {e}")
