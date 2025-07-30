import base64
import io
import json
from typing import Any, AsyncGenerator, cast, Dict, List, Optional

from .http_client import HttpClient
from .http_client import ResponseWrapper
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
    def audioConfig(self) -> Optional[AudioConfig]:
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
    def modelId(self) -> Optional[str]:
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
    ) -> Dict[str, Any]:
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

        response = await self.__client.request(
            "post",
            "/tts/v1alpha/text:synthesize-sync",
            data=data,
        )
        return cast(Dict[str, Any], response)

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

        audio_content = response.get("audioContent")
        if not audio_content:
            raise ValueError("No audio content in response")
        decoded_audio = base64.b64decode(audio_content)

        return io.BytesIO(decoded_audio)

    async def synthesizeSpeechStream(
        self,
        input: str,
        voice: Optional[TTSVoices] = None,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
        audioConfig: Optional[AudioConfig] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
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

        response: Optional[ResponseWrapper] = None
        try:
            response = cast(
                ResponseWrapper,
                await self.__client.request(
                    "post",
                    "/tts/v1alpha/text:synthesize",
                    data=data,
                    stream=True,
                ),
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
                audio_content = chunk.get("audioContent")
                if audio_content is not None:
                    decoded_audio = base64.b64decode(audio_content)
                    yield io.BytesIO(decoded_audio)
        except Exception:
            raise

    async def voices(
        self,
        languageCode: Optional[TTSLanguageCodes] = None,
        modelId: Optional[str] = None,
    ) -> List[VoiceResponse]:
        """Get voices"""
        data: Dict[str, Any] = {}
        if languageCode:
            data["languageCode"] = languageCode
        if modelId:
            data["modelId"] = modelId

        response = await self.__client.request("get", "/tts/v1alpha/voices", data=data)
        voices = response.get("voices", [])
        return cast(List[VoiceResponse], voices)
