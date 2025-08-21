"""
FIAP Authentication Module

This module handles authentication with FIAP platform,
including session management and credential validation.
"""

import os
import logging
import aiohttp
import asyncio
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class FIAPSession:
    """
    Manages FIAP session including authentication and basic session operations.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.sesskey: Optional[str] = None
        self.is_authenticated = False
        self.login_url = os.getenv("FIAP_LOGIN_URL")
        self.api_base = os.getenv("FIAP_API_BASE")

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def login(self, username: str, password: str, max_retries: int = 3) -> bool:
        """
        Authenticate with FIAP platform.

        Args:
            username: FIAP username
            password: FIAP password
            max_retries: Maximum number of login attempts

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        for attempt in range(1, max_retries + 1):
            logger.info(f"Login attempt {attempt}/{max_retries}")

            try:
                # Prepare login data
                login_data = {
                    'username': username,
                    'password': password
                }

                # Send login request
                async with self.session.post(
                        self.login_url,
                        data=login_data,
                        headers={
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1'
                        }
                ) as response:

                    text_response = await response.text()

                    # Check for invalid credentials
                    if "Invalid username or password" in text_response or "Usuário ou senha inválidos" in text_response:
                        logger.warning(f"Invalid credentials on attempt {attempt}")
                        if attempt == max_retries:
                            logger.error("All login attempts failed - invalid credentials")
                            return False
                        continue

                    # Check if login was successful and extract sesskey from cookies
                    if response.status == 200:
                        # Get sesskey from cookies
                        cookies = self.session.cookie_jar
                        sesskey = None

                        # Find sesskey cookie
                        for cookie in cookies:
                            if cookie.key == 'sesskey':
                                sesskey = cookie.value
                                break

                        if sesskey:
                            self.sesskey = sesskey
                            self.is_authenticated = True

                            logger.info(f"Successfully authenticated with FIAP (sesskey: {sesskey[:10]}...)")
                            logger.info(f"Stored {len(cookies)} cookies from login")

                            # Debug: log important cookies
                            important_cookies = ['MoodleSession', 'MOODLEID1_', 'sesskey']
                            for cookie in cookies:
                                if cookie.key in important_cookies:
                                    logger.debug(f"Important cookie: {cookie.key}={cookie.value[:10]}...")

                            return True
                        else:
                            logger.warning("Could not find sesskey in cookies")
                            # Log all cookies for debugging
                            logger.debug("Available cookies:")
                            for cookie in cookies:
                                logger.debug(f"  {cookie.key}={cookie.value[:20]}...")

            except Exception as e:
                logger.error(f"Login attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    logger.error("All login attempts failed due to errors")
                    return False

                # Wait before retry
                await asyncio.sleep(2)

        return False


async def authenticate_fiap(username: str = None, password: str = None, max_retries: int = 3) -> Tuple[
    bool, Optional[FIAPSession]]:
    """
    Convenience function to authenticate with FIAP.

    Args:
        username: FIAP username (defaults to env var)
        password: FIAP password (defaults to env var)
        max_retries: Maximum login attempts

    Returns:
        Tuple[bool, Optional[FIAPSession]]: Success status and session object
    """
    if not username:
        username = os.getenv('FIAP_USERNAME')
    if not password:
        password = os.getenv('FIAP_PASSWORD')

    if not username or not password:
        logger.error("FIAP credentials not provided")
        return False, None

    session = FIAPSession()
    await session.__aenter__()

    success = await session.login(username, password, max_retries)

    if success:
        return True, session
    else:
        await session.__aexit__(None, None, None)
        return False, None
