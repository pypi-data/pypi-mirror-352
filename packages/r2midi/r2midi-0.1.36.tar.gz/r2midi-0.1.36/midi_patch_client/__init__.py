"""
MIDI Patch Selection Client

A client application for selecting and controlling MIDI patches.
"""

from .api_client import CachedApiClient
from .models import Device, Patch, UIState

__version__ = "0.1.0"
__all__ = ['CachedApiClient', 'Device', 'Patch', 'UIState']