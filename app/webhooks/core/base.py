"""
Base Webhook Classes

Contains the base webhooks class and common interfaces to avoid circular imports.
"""

import logging


class BaseWebhook:
    """
    Base class for all webhooks implementations.
    """

    def __init__(self, bot, webhook_type: str):
        """
        Initialize base webhooks.

        Args:
            bot: Discord bot instance
            webhook_type: Type identifier for this webhooks
        """
        self.bot = bot
        self.webhook_type = webhook_type
        self.last_execution = None
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    async def execute(self, **kwargs) -> bool:
        """
        Execute webhooks logic. Must be implemented by subclasses.

        Args:
            **kwargs: Webhook-specific parameters

        Returns:
            bool: True if execution was successful
        """
        raise NotImplementedError("Subclasses must implement execute() method")

    async def validate_config(self) -> bool:
        """
        Validate webhooks configuration. Can be overridden by subclasses.

        Returns:
            bool: True if configuration is valid
        """
        return True

    async def shutdown(self):
        """Clean shutdown of webhooks. Can be overridden by subclasses."""
        self.logger.info(f"Shutting down {self.webhook_type} webhooks")


# Webhook registry for dynamic loading
WEBHOOK_REGISTRY = {
    'sync_calendar': 'app.webhooks.sync_calendar.app.CalendarSyncWebhook'
}


def get_available_webhooks() -> list:
    """
    Get list of available webhooks types.

    Returns:
        list: Available webhooks type names
    """
    return list(WEBHOOK_REGISTRY.keys())
