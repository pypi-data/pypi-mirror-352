import base64
import io
import json
from typing import AsyncGenerator, Optional

from .http_client import HttpClient
from .typings.tts import AudioConfig
from .typings.tts import TTSLanguageCodes
from .typings.tts import TTSVoices
from .typings.tts import VoiceResponse


class TTS:
    """TTS API client"""

    def __init__(
        self,
        client: HttpClient,
        audioConfig: Optional[AudioConfig] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        voice: Optional[TTSVoices] = None,
    ):
        """Constructor for TTS class"""
        self.__audioConfig = audioConfig or None
        self.__client = client
        self.__languageCode = languageCode or "en-US"
        self.__modelId = modelId or None
        self.__voice = voice or "Emma"

    @property
    def audioConfig(self) -> AudioConfig:
        """Get default audio config"""
        return self.__audioConfig

    @audioConfig.setter
    def audioConfig(self, audioConfig: AudioConfig):
        """Set default audio config"""
        self.__audioConfig = audioConfig

    @property
    def languageCode(self) -> TTSLanguageCodes:
        """Get default language code"""
        return self.__languageCode

    @languageCode.setter
    def languageCode(self, languageCode: TTSLanguageCodes):
        """Set default language code"""
        self.__languageCode = languageCode

    @property
    def modelId(self) -> str:
        """Get default model ID"""
        return self.__modelId

    @modelId.setter
    def modelId(self, modelId: str):
        """Set default model ID"""
        self.__modelId = modelId

    @property
    def voice(self) -> TTSVoices:
        """Get default voice"""
        return self.__voice

    @voice.setter
    def voice(self, voice: TTSVoices):
        """Set default voice"""
        self.__voice = voice

    async def synthesizeSpeech(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> dict:
        """Synthesize speech"""
        data = {
            "input": {"text": input},
            "voice": {
                "name": voice or self.__voice,
                "languageCode": languageCode or self.__languageCode,
            },
        }

        if audioConfig or self.__audioConfig:
            data["audioConfig"] = audioConfig or self.__audioConfig

        if modelId or self.__modelId:
            data["modelId"] = modelId or self.__modelId

        return await self.__client.request(
            "post",
            "/tts/v1alpha/text:synthesize-sync",
            data=data,
        )

    async def synthesizeSpeechAsWav(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> io.BytesIO:
        """Synthesize speech as WAV response"""
        if audioConfig is not None:
            audioConfig["audioEncoding"] = "AUDIO_ENCODING_UNSPECIFIED"

        response = await self.synthesizeSpeech(
            input=input,
            voice=voice,
            languageCode=languageCode,
            modelId=modelId,
            audioConfig=audioConfig,
        )

        decoded_audio = base64.b64decode(response.get("audioContent"))

        return io.BytesIO(decoded_audio)

    async def synthesizeSpeechStream(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> AsyncGenerator[dict, None]:
        """Synthesize speech as a stream"""
        data = {
            "input": {"text": input},
            "voice": {
                "name": voice or self.__voice,
                "languageCode": languageCode or self.__languageCode,
            },
        }

        if audioConfig or self.__audioConfig:
            data["audioConfig"] = audioConfig or self.__audioConfig

        if modelId or self.__modelId:
            data["modelId"] = modelId or self.__modelId

        response = None
        try:
            response = await self.__client.request(
                "post",
                "/tts/v1alpha/text:synthesize",
                data=data,
                stream=True,
            )

            async for chunk in response.content:
                if chunk:
                    chunk_data = json.loads(chunk)
                    if isinstance(chunk_data, dict) and chunk_data.get("result"):
                        yield chunk_data["result"]
        except Exception:
            raise
        finally:
            if response is not None:
                await response.close()

    async def synthesizeSpeechStreamAsWav(
        self,
        input: str,
        modelId: Optional[str] = None,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> AsyncGenerator[io.BytesIO, None]:
        """Synthesize speech as WAV response from streamed data"""
        if audioConfig is not None:
            audioConfig["audioEncoding"] = "AUDIO_ENCODING_UNSPECIFIED"

        try:
            async for chunk in self.synthesizeSpeechStream(
                input=input,
                modelId=modelId,
                voice=voice,
                languageCode=languageCode,
                audioConfig=audioConfig,
            ):
                if chunk and chunk.get("audioContent") is not None:
                    decoded_audio = base64.b64decode(chunk.get("audioContent"))
                    yield io.BytesIO(decoded_audio)
        except Exception:
            raise

    async def voices(
        self,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
    ) -> list[VoiceResponse]:
        """Get voices"""
        data = {}
        if languageCode:
            data["languageCode"] = languageCode
        if modelId:
            data["modelId"] = modelId

        response = await self.__client.request("get", "/tts/v1alpha/voices", data=data)
        return response.get("voices")
