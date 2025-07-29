"""
NomadicML Python SDK for the DriveMonitor API.

This SDK provides a simple interface to interact with the 
DriveMonitor backend for analyzing driving videos.
"""

__version__ = "0.0.2"  # This will be the clean version for PyPI
__build__ = "42268eb"      # This will hold the commit hash or full build string, populated by CI

from .client import NomadicML
from .video import VideoClient
from .exceptions import NomadicMLError, AuthenticationError, APIError, VideoUploadError, AnalysisError
from .types import VideoSource, ProcessingStatus, Severity, convert_to_upload_analyze_response_subset

# Add video client to NomadicML
def _add_video_client(client):
    client.video = VideoClient(client)
    return client

# Patch the NomadicML class
_original_init = NomadicML.__init__

def _patched_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    _add_video_client(self)

NomadicML.__init__ = _patched_init

__all__ = [
    "NomadicML",
    "VideoClient",
    "NomadicMLError",
    "AuthenticationError",
    "APIError",
    "VideoUploadError",
    "AnalysisError",
    "VideoSource",
    "ProcessingStatus",
    "EventType",
    "Severity",
    "convert_to_upload_analyze_response_subset",
]
