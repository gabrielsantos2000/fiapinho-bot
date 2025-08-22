"""
Bot Cogs Package

Contains organized command groups (cogs) for the Fiapinho bot.
"""

from .fiap import FiapinhoCog
from .utility import UtilityCog

__all__ = [
    'FiapinhoCog',
    'UtilityCog'
]