"""
Calendar Sync Webhook for FIAP Events

This module handles the synchronization of FIAP calendar events,
including authentication, data retrieval, storage, and Discord notifications.
"""

import os
import json
import logging
import asyncio
import validators
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Coroutine

import discord
from discord import Embed

from app.webhooks.core.fiap_auth import FIAPSession, authenticate_fiap
from .evens_api import FIAPCalendarAPI
from app.webhooks.core.base import BaseWebhook
from app.utils.format_datetime import get_all_days_in_month
from app.enum.colors import StatusColors, FiapColors
from app.utils.discord.notifications import FiapinhoNotification

logger = logging.getLogger(__name__)


class CalendarSyncWebhook(BaseWebhook):
    """
    Handles synchronization of FIAP calendar events.
    """

    def __init__(self, bot):
        """
        Initialize calendar sync webhooks.

        Args:
            bot: Discord bot instance
        """
        super().__init__(bot, 'sync_calendar')
        self.data_dir = Path('app/database')
        self.data_dir.mkdir(exist_ok=True)
        self.src_images = Path('src/images')
        self.src_images.mkdir(exist_ok=True)
        self.session: Optional[FIAPSession] = None
        self.api: Optional[FIAPCalendarAPI] = None
        self.notifications: Optional[List[FiapinhoNotification]] = None

    async def execute(self, **kwargs) -> bool:
        """
        Execute calendar synchronization process.

        Args:
            **kwargs: Additional parameters

        Returns:
            bool: True if sync was successful
        """

        try:
            self.logger.info("Starting calendar synchronization...")
            self.last_execution = datetime.now()

            # Step 1: Authenticate with FIAP
            success, session = await authenticate_fiap(
                max_retries=int(os.getenv('MAX_LOGIN_RETRIES', '3'))
            )

            self.notifications = FiapinhoNotification(self.bot)
            if not success:
                await self.notifications.send_auth_failure_notification()
                return False

            self.session = session
            self.api = FIAPCalendarAPI(session)
            self.logger.info("FIAP authentication successful")

            # Step 2: Retrieve calendar events
            events_data = await self._fetch_calendar_events(kwargs.get("resync", False))
            if not events_data:
                self.logger.warning("No events data retrieved")
                return False

            # Step 3: Process and store events
            new_events = await self._process_events(events_data)

            # Step 4: Fetch detailed information for new events
            updated_events = await self._fetch_event_details(new_events)

            # Step 5: Send notifications for new/updated events
            if updated_events:
                await self._send_event_notifications(updated_events)

            # Step 6: Clean up
            await self._cleanup()

            self.logger.info("Calendar synchronization completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error in calendar sync: {e}")
            await self._send_error_notification(str(e))
            return False

    async def _fetch_calendar_events(self, resync: bool = False) -> Optional[Dict[str, Any]]:
        """
        Fetch calendar events from FIAP API using the panel events endpoint.

        Returns:
            Optional[Dict[str, Any]]: Events data or None if failed
        """
        try:
            if not self.session:
                raise RuntimeError("No active FIAP session")

            # Try the panel events endpoint first (for today's events)
            self.logger.info("Fetching today's calendar panel events from FIAP...")
            events_data = await self.api.get_calendar_panel_events()
            #events_data = await self.api.get_calendar_events()

            if 'error' in events_data or resync:
                msg = f"Panel events API error: {events_data['error']}" if not resync else "Resync calendar events"
                self.logger.warning(msg)

                # Fallback to get panel events for all days in the current month
                self.logger.info("Fetching panel events for all days in current month...")
                events_data = await self._fetch_monthly_panel_events()

                if not events_data or 'error' in events_data:
                    self.logger.error("Failed to fetch monthly panel events")
                    return None

            # Handle the new response format
            events = []

            # The response should be a list with the first element containing the data
            if isinstance(events_data, list) and len(events_data) > 0:
                response_item = events_data[0]

                if isinstance(response_item, dict) and not response_item.get('error', False):
                    if 'data' in response_item:
                        events = response_item['data']
                        self.logger.info(f"Retrieved {len(events)} calendar events for current month")
                    else:
                        self.logger.warning(f"Unexpected response structure: {list(response_item.keys())}")
                else:
                    error_msg = response_item.get('error', 'Unknown error') \
                        if isinstance(response_item, dict) else str(response_item)
                    self.logger.error(f"API returned error: {error_msg}")
                    return None
            else:
                self.logger.warning(f"Unexpected response format: {type(events_data)}")
                return None

            # Return in expected format
            return {
                'events': events,
                'success': True
            }

        except Exception as e:
            self.logger.error(f"Error fetching calendar events: {e}")
            return None

    async def _fetch_monthly_panel_events(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch calendar panel events for all days in the current month.

        Returns:
            Optional[List[Dict[str, Any]]]: List of all events for the month or None if failed
        """
        try:
            if not self.session or not self.api:
                raise RuntimeError("No active FIAP session or API")

            # Get all days in the current month as timestamps
            day_timestamps = get_all_days_in_month()
            all_events = []
            seen_event_ids = set()

            self.logger.info(f"Fetching panel events for {len(day_timestamps)} days in current month...")

            for i, day_timestamp in enumerate(day_timestamps):
                try:
                    self.logger.info(f"Fetching events for day {i+1}/{len(day_timestamps)} (timestamp: {day_timestamp})")
                    
                    # Get panel events for this specific day
                    day_events_data = await self.api.get_calendar_panel_events(time_search=day_timestamp)
                    
                    if 'error' in day_events_data:
                        self.logger.warning(f"Error fetching events for day {i+1}: {day_events_data['error']}")
                        continue

                    # Process the response format
                    if isinstance(day_events_data, list) and len(day_events_data) > 0:
                        response_item = day_events_data[0]
                        
                        if isinstance(response_item, dict) and not response_item.get('error', False):
                            day_events = []
                            if 'data' in response_item:
                                day_events = response_item['data']
                            elif isinstance(response_item, dict):
                                day_events = [response_item]  # Single event case
                            
                            # Add events to the collection, avoiding duplicates
                            for event in day_events:
                                event_id = event.get('id')
                                if event_id and event_id not in seen_event_ids:
                                    all_events.append(event)
                                    seen_event_ids.add(event_id)
                                    
                            if day_events:
                                self.logger.info(f"Found {len(day_events)} events for day {i+1} (total: {len(all_events)})")
                        else:
                            error_msg = response_item.get('error', 'Unknown error') if isinstance(response_item, dict) else str(response_item)
                            self.logger.warning(f"API returned error for day {i+1}: {error_msg}")
                    
                    # Add delay to avoid overwhelming the API
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing day {i+1}: {e}")
                    continue

            self.logger.info(f"Retrieved {len(all_events)} total unique events from monthly scan")
            
            # Return in the expected format
            return [{
                'data': all_events,
                'error': False
            }]

        except Exception as e:
            self.logger.error(f"Error fetching monthly panel events: {e}")
            return None

    async def _process_events(self, events_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process events data and identify new events.

        Args:
            events_data: Raw events data from FIAP API

        Returns:
            List[Dict[str, Any]]: List of new events to process
        """
        try:
            events = events_data.get('events', [])
            if not events:
                self.logger.info("No events found in events_data")
                return []

            self.logger.info(f"Processing {len(events)} total events from API")

            # Load existing events
            existing_events = await self._load_existing_events()

            existing_ids = {event.get('id') for event in existing_events if event.get('id')}
            self.logger.info(f"Found {len(existing_ids)} existing events in database")

            # Deduplicate events from the API response first (in case of duplicates from multiple day queries)
            unique_events = {}
            for event in events:
                event_id = event.get('id')
                if event_id:
                    if event_id not in unique_events:
                        unique_events[event_id] = event
                    # Keep the event with more complete data (more keys)
                    elif len(event) > len(unique_events[event_id]):
                        unique_events[event_id] = event

            events = list(unique_events.values())
            self.logger.info(f"After deduplication: {len(events)} unique events")

            # Filter new events
            new_events = []
            for event in events:
                event_id = event.get('id')
                if event_id and event_id not in existing_ids:
                    new_events.append(event)
                    self.logger.debug(f"New event found: {event_id} - {event.get('content', 'No title')}")
                elif event_id:
                    self.logger.debug(f"Existing event: {event_id} - {event.get('content', 'No title')}")
                else:
                    self.logger.warning(f"Event without ID found: {event}")

            # Combine existing events with new unique events for storage
            all_events_for_storage = []
            
            # Add existing events first
            existing_event_ids = set()
            for existing_event in existing_events:
                existing_id = existing_event.get('id')
                if existing_id:
                    all_events_for_storage.append(existing_event)
                    existing_event_ids.add(existing_id)
            
            # Add new events that don't already exist
            for event in events:
                event_id = event.get('id')
                if event_id and event_id not in existing_event_ids:
                    all_events_for_storage.append(event)
                elif event_id and event_id in existing_event_ids:
                    # Update existing event with potentially newer data
                    for i, existing_event in enumerate(all_events_for_storage):
                        if existing_event.get('id') == event_id:
                            all_events_for_storage[i] = event
                            break

            # Save all events (existing + new/updated)
            await self._save_events(all_events_for_storage)

            self.logger.info(f"Found {len(new_events)} new events to process")
            self.logger.info(f"Saved {len(all_events_for_storage)} total events to database")
            return new_events

        except Exception as e:
            self.logger.error(f"Error processing events: {e}")
            return []

    async def _fetch_event_details(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for events.

        Args:
            events: List of events to get details for

        Returns:
            List[Dict[str, Any]]: Events with detailed information
        """
        updated_events = []

        for event in events:
            try:
                event_id = event.get('id')
                event_type = event.get('type')
                event_module = event.get('module') if event.get('module') else "conteudosexternos"

                if not event_id or not event_type:
                    # If we don't have both id and type, we can't fetch details
                    self.logger.warning(f"Event missing id or type: {event}")
                    updated_events.append(event)
                    continue

                self.logger.info(f"Fetching details for event {event_id} (type: {event_type})")

                # API to get unit event details
                details = await self.api.get_calendar_event(
                    event_type=event_type,
                    event_id=str(event_id),
                    module_name=event_module
                )

                if 'error' not in details:
                    # Handle the response format (should be list with data)
                    if isinstance(details, list) and len(details) > 0:
                        detail_item = details[0]
                        if isinstance(detail_item, dict) and not detail_item.get('error', False):
                            # Merge basic event info with detailed info
                            if 'data' in detail_item:
                                event.update(detail_item['data'])
                            else:
                                event.update(detail_item)

                            if 'local' in event:
                                self.logger.info(f"Found local info for event {event_id}")
                        else:
                            error_msg = detail_item.get('error', 'Unknown error') if isinstance(detail_item, dict) else str(detail_item)
                            self.logger.warning(f"API returned error for event {event_id}: {error_msg}")
                    else:
                        self.logger.warning(f"Unexpected details response format for event {event_id}")

                    updated_events.append(event)
                else:
                    self.logger.warning(f"Could not get details for event {event_id}: {details.get('error')}")
                    # Still add the basic event info
                    updated_events.append(event)

                # Add delay to avoid overwhelming the API
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error fetching details for event {event.get('id', 'unknown')}: {e}")
                # Add the basic event even if details failed
                updated_events.append(event)

        # Update stored events with detailed information
        if updated_events:
            await self._update_stored_events(updated_events)

        return updated_events

    async def _load_existing_events(self) -> List[Dict[str, Any]]:
        """
        Load existing events from storage.

        Returns:
            List[Dict[str, Any]]: Existing events
        """
        try:
            now = datetime.now()
            filename = self.data_dir / f"events_{now.month:02d}_{now.year}.json"

            if filename.exists():
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return []

        except Exception as e:
            self.logger.error(f"Error loading existing events: {e}")
            return []

    async def _save_events(self, events: List[Dict[str, Any]]):
        """
        Save events to monthly file.

        Args:
            events: Events to save
        """
        try:
            now = datetime.now()
            filename = self.data_dir / f"events_{now.month:02d}_{now.year}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"Saved {len(events)} events to {filename}")

        except Exception as e:
            self.logger.error(f"Error saving events: {e}")

    async def _update_stored_events(self, updated_events: List[Dict[str, Any]]):
        """
        Update stored events with new detailed information.

        Args:
            updated_events: Events with updated information
        """
        try:
            existing_events = await self._load_existing_events()

            # Create a map for quick lookup
            updated_map = {}
            for event in updated_events:
                event_id = event.get('id')
                if event_id:
                    updated_map[event_id] = event

            # Update existing events
            for i, event in enumerate(existing_events):
                event_id = event.get('id')
                if event_id in updated_map:
                    existing_events[i] = updated_map[event_id]

            await self._save_events(existing_events)

        except Exception as e:
            self.logger.error(f"Error updating stored events: {e}")

    async def _send_event_notifications(self, events: List[Dict[str, Any]]):
        """
        Send Discord notifications for new events.

        Args:
            events: Events to notify about
        """
        try:
            channel_id = os.getenv('DISCORD_CALENDAR_CHANNEL_ID')
            if not channel_id:
                self.logger.warning("No Discord channel configured for notifications")
                return

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                self.logger.error(f"Could not find Discord channel: {channel_id}")
                return

            for event in events:
                embed, images = await self._create_event_embed(event)
                await channel.send("📅 **Novo evento FIAP detectado!**", embed=embed, files=images)

                # Add delay between messages
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Error sending event notifications: {e}")


    async def _create_event_embed(self, event: Dict[str, Any]) -> tuple[Embed, list[Any]]:
        """
        Create Discord embed for an event.

        Args:
            event: Event data

        Returns:
            Embed: Discord embed object
        """
        # Handle different possible field names
        title = event.get('content', event.get('name', 'Evento sem título'))
        description = event.get('description', 'Sem descrição disponível')

        # Truncate description if too long
        if len(description) > 2048:
            description = description[:2045] + "..."

        embed = Embed(
            title=title,
            description=description,
            color=FiapColors.RED.value,
            timestamp=datetime.now()
        )

        # Add event details - handle both timeopen and timestart
        start_time = event.get('timeopen')
        end_time = event.get('timeclose')
        if start_time:
            try:
                if isinstance(start_time, (int, float)):
                    start_dt = datetime.fromtimestamp(start_time)
                    end_dt = datetime.fromtimestamp(end_time)

                    embed.add_field(
                        name="📅 Data/Hora",
                        value=f'{start_dt.strftime("%d/%m/%Y às %H:%M")} até {end_dt.strftime("%H:%M")}',
                        inline=True
                    )
            except Exception:
                pass

        # Add formatted dates if available
        formatted_date = event.get('timeopen_formated')
        if formatted_date and not start_time:
            embed.add_field(
                name="📅 Data",
                value=formatted_date,
                inline=True
            )

        # Add event type
        event_type = event.get('type')
        if event_type:
            embed.add_field(
                name="📋 Tipo",
                value="🛑 LIVE" if event_type == "Live" else event_type,
                inline=True
            )

        # Add course name if available
        course_name = event.get('course_name')
        if course_name:
            embed.add_field(
                name="📚 Curso",
                value=course_name,
                inline=False
            )

        local = event.get('local')
        self.logger.info(f"{event}")
        teams_link = None
        if validators.url(local):
            teams_link = local

        if teams_link:
            embed.add_field(
                name="🎥 Link da Transmissão",
                value=f"[Clique aqui para acessar]({teams_link})",
                inline=False
            )

        event_id = event.get('id')
        if event_id:
            embed.set_footer(text=f"ID do Evento: {event_id}")

        images = [
            discord.File(self.src_images / "fiap-on.webp", filename=f"fiap-on.webp"),
            discord.File(self.src_images / "banner-fiap.png", filename=f"banner-fiap.png")
        ]

        embed.set_image(url="attachment://banner-fiap.png")
        embed.set_thumbnail(url="attachment://fiap-on.webp")

        return embed, images

    async def _send_error_notification(self, error_message: str):
        """
        Send notification about sync error.

        Args:
            error_message: Error message to include
        """
        try:
            channel_id = os.getenv('DISCORD_CALENDAR_CHANNEL_ID')
            if not channel_id:
                return

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return

            embed = Embed(
                title="⚠️ Erro na Sincronização do Calendário",
                description=f"Ocorreu um erro durante a sincronização: {error_message}",
                color=StatusColors.ALERT.value,
                timestamp=datetime.now()
            )

            await channel.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error sending error notification: {e}")

    async def _cleanup(self):
        """Clean up resources."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def shutdown(self):
        """Clean shutdown of calendar sync webhooks."""
        await super().shutdown()
        await self._cleanup()
