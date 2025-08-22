"""
FIAP Event Calendar API Module

This module handles calendar-specific API operations for FIAP events,
including fetching calendar events, panel events, and event details.
"""

import json
import logging
from typing import Dict, Any, List
from urllib.parse import urlencode

from app.webhooks.core.fiap_auth import FIAPSession
from app.utils.format_datetime import get_month_range_timestamps, get_date_timestamp

logger = logging.getLogger(__name__)


class FIAPCalendarAPI:
    """
    FIAP Calendar API operations.
    Extends FIAPSession with calendar-specific functionality.
    """

    def __init__(self, session: FIAPSession):
        """
        Initialize with an authenticated FIAPSession.

        Args:
            session: Authenticated FIAPSession instance
        """
        if not session.is_authenticated:
            raise RuntimeError("Session must be authenticated before use")

        self.session = session

    async def get_calendar_events(self, time_open: int = None, time_close: int = None,
                                  filter_id: Any = None, events_filter: List = None) -> Dict[str, Any]:
        """
        Retrieve calendar events from FIAP for a specific date range.

        Args:
            time_open: Start timestamp (defaults to start of current month)
            time_close: End timestamp (defaults to end of current month)
            filter_id: Filter ID (defaults to null)
            events_filter: Events filter array (defaults to empty list)

        Returns:
            Dict[str, Any]: API response data
        """
        if not self.session.is_authenticated or not self.session.sesskey:
            raise RuntimeError("Not authenticated. Session must be logged in.")

        # Default to current month if timestamps not provided
        if time_open is None or time_close is None:
            time_open, time_close = get_month_range_timestamps()

        payload = [
            {
                "index": 0,
                "methodname": "local_calendar_get_calendar_events",
                "args": {
                    "time_open": time_open,
                    "time_close": time_close,
                    "filter_id": filter_id,
                    "events_filter": events_filter or []
                }
            }
        ]

        return await self._make_api_request_json(payload)

    async def get_calendar_panel_events(self, time_search: int = None,
                                        filter_id: Any = None, events_filter: List = None) -> Dict[str, Any]:
        """
        Retrieve calendar panel events from FIAP for a specific date.

        Args:
            time_search: Search timestamp for specific date (defaults to today)
            filter_id: Filter ID (defaults to null)
            events_filter: Events filter array (defaults to empty list)

        Returns:
            Dict[str, Any]: API response data
        """
        if not self.session.is_authenticated or not self.session.sesskey:
            raise RuntimeError("Not authenticated. Session must be logged in.")

        # Default to today if timestamp not provided
        if time_search is None:
            time_search = get_date_timestamp()

        payload = [
            {
                "index": 0,
                "methodname": "local_calendar_get_calendar_pannel_events",
                "args": {
                    "time_search": time_search,
                    "filter_id": filter_id,
                    "events_filter": events_filter or []
                }
            }
        ]

        return await self._make_api_request_json(payload)

    async def get_calendar_event(self, event_type: str, event_id: str,
                                 module_name: str = "conteudosexternos") -> Dict[str, Any]:
        """
        Retrieve specific calendar event details.

        Args:
            event_type: Type of the event (e.g., "Live", "Schedule")
            event_id: ID of the event to retrieve
            module_name: Module name (defaults to "conteudosexternos")

        Returns:
            Dict[str, Any]: API response data
        """
        if not self.session.is_authenticated or not self.session.sesskey:
            raise RuntimeError("Not authenticated. Session must be logged in.")

        payload = [
            {
                "index": 0,
                "methodname": "local_calendar_get_calendar_event",
                "args": {
                    "event_type": event_type,
                    "event_id": event_id,
                    "module_name": module_name
                }
            }
        ]

        return await self._make_api_request_json(payload)

    async def _make_api_request_json(self, payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make an authenticated JSON POST API request to FIAP.

        Args:
            payload: JSON payload to send

        Returns:
            Dict[str, Any]: API response data
        """
        if not self.session.session:
            raise RuntimeError("Session not initialized")

        try:
            url = f"{self.session.api_base}?sesskey={self.session.sesskey}"

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://on.fiap.com.br/',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest'
            }

            logger.debug(f"Making JSON POST API request to: {url}")
            logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
            logger.debug(f"Current cookies: {len(self.session.session.cookie_jar)} cookies")

            async with self.session.session.post(url, json=payload, headers=headers) as response:

                if response.status != 200:
                    logger.error(f"API request failed with status {response.status}")
                    text_response = await response.text()
                    logger.error(f"Response content: {text_response[:500]}...")
                    return {'error': f'HTTP {response.status}', 'response': text_response}

                try:
                    data = await response.json()
                    logger.debug(f"API response: {json.dumps(data, ensure_ascii=False)[:200]}...")
                    return data
                except json.JSONDecodeError:
                    text_data = await response.text()
                    logger.error(f"Invalid JSON response: {text_data[:500]}...")
                    return {'error': 'Invalid JSON response', 'raw_response': text_data}

        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {'error': str(e)}
