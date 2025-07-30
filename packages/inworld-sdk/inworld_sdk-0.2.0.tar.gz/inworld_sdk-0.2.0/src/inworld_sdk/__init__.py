"""
Inworld AI SDK - A Python SDK for Inworld AI
"""

__version__ = "0.2.0"

from typing import Literal, Optional

from .http_client import HttpClient
from .tts import TTS
from .typings.tts import TTSAudioEncoding
from .typings.tts import TTSLanguageCodes
from .typings.tts import TTSVoices

__all__ = ["InworldAIClient", "TTSAudioEncoding", "TTSLanguageCodes", "TTSVoices"]


class InworldAIClient:
    """Client for interacting with Inworld AI's services."""

    def __init__(
        self,
        api_key: str,
        auth_type: Optional[Literal["basic", "bearer"]] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the Inworld AI client.

        Args:
            api_key: Your Inworld AI API key
            auth_type: Optional authentication type, defaults to "basic"
            base_url: Optional custom base URL for the API, defaults to https://api.inworld.ai/v1
        """
        client = HttpClient(api_key, auth_type, base_url)
        self.__tts = TTS(client)

    @property
    def tts(self) -> TTS:
        return self.__tts
