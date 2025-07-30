"""
🎨 Python Midjourney - Midjourney automation via Discord
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Midjourney automation system using Discord user tokens"

from .client import MidjourneyClient, quick_generate

__all__ = ['MidjourneyClient', 'quick_generate'] 
