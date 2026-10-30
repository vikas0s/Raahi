"""
Sarvam AI Integration Service for Raahi.
Provides secure, server-side communication with Sarvam AI:
- Chat Completions (sarvam-105b / sarvam-105b-conversations)
- Speech-to-Text (saaras:v4)
- Text-to-Speech (bulbul:v4-flash)
"""
import os
import logging
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("raahi.sarvam")

SARVAM_CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

DEFAULT_MODEL = os.getenv("SARVAM_MODEL", "sarvam-105b")
DEFAULT_TIMEOUT_SEC = 12.0

class SarvamConfigurationError(Exception):
    """Raised when SARVAM_API_KEY is missing or invalid in environment."""
    pass

class SarvamAPIError(Exception):
    """Raised when the Sarvam API returns an HTTP error or malformed response."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class SarvamAIService:
    def __init__(self):
        self._default_model = DEFAULT_MODEL

    @property
    def api_key(self) -> str:
        key = os.getenv("SARVAM_API_KEY", "").strip()
        return key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:
        """
        Calls Sarvam AI Chat Completions API with the given messages.
        Headers require `api-subscription-key: <KEY>`.
        """
        key = self.api_key
        if not key:
            raise SarvamConfigurationError(
                "SARVAM_API_KEY is not configured in backend environment (.env). "
                "Please configure your Sarvam API subscription key to enable AI conversation."
            )

        target_model = model or os.getenv("SARVAM_MODEL", self._default_model)

        headers = {
            "api-subscription-key": key,
            "Content-Type": "application/json"
        }

        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SEC) as client:
                res = await client.post(SARVAM_CHAT_URL, headers=headers, json=payload)
        except httpx.TimeoutException:
            logger.error("Sarvam AI chat request timed out after %.1f seconds", DEFAULT_TIMEOUT_SEC)
            raise SarvamAPIError("Request to Sarvam AI timed out. Please try again in a moment.", status_code=504)
        except httpx.RequestError as exc:
            logger.error("Network error communicating with Sarvam AI: %s", exc)
            raise SarvamAPIError(f"Network error communicating with Sarvam AI: {str(exc)}", status_code=502)

        if res.status_code == 401 or res.status_code == 403:
            logger.error("Sarvam AI authentication failed: HTTP %s", res.status_code)
            raise SarvamAPIError(
                "Invalid or unauthorized Sarvam API key. Please verify SARVAM_API_KEY in your server configuration.",
                status_code=res.status_code,
                response_body=res.text
            )
        elif res.status_code == 429:
            logger.warning("Sarvam AI rate limit or quota exceeded: %s", res.text)
            raise SarvamAPIError(
                "Sarvam AI rate limit or quota limit reached. Please wait a moment and try again.",
                status_code=429,
                response_body=res.text
            )
        elif res.status_code >= 500:
            logger.error("Sarvam AI upstream error %s: %s", res.status_code, res.text)
            raise SarvamAPIError(
                "Sarvam AI service is temporarily experiencing upstream issues. Please retry shortly.",
                status_code=res.status_code,
                response_body=res.text
            )
        elif not res.is_success:
            logger.error("Sarvam AI returned error %s: %s", res.status_code, res.text)
            raise SarvamAPIError(
                f"Sarvam AI API error (HTTP {res.status_code}): {res.text}",
                status_code=res.status_code,
                response_body=res.text
            )

        try:
            data = res.json()
            choices = data.get("choices", [])
            if not choices:
                raise SarvamAPIError("Sarvam AI response contained no choices.", status_code=res.status_code)
            content = (choices[0].get("message", {}).get("content") or "").strip()
            return content
        except Exception as exc:
            logger.error("Failed to parse Sarvam AI JSON response: %s", exc)
            raise SarvamAPIError("Received an invalid response format from Sarvam AI.", status_code=500)

    async def transcribe_speech(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language_code: str = "unknown"
    ) -> str:
        """
        Transcribes speech audio using Sarvam Saaras model.
        Returns transcribed text.
        """
        key = self.api_key
        if not key:
            raise SarvamConfigurationError("SARVAM_API_KEY is not configured for speech recognition.")

        headers = {
            "api-subscription-key": key
        }

        # Determine MIME type based on filename extension
        mime_type = "audio/wav"
        if filename.endswith(".mp3"):
            mime_type = "audio/mpeg"
        elif filename.endswith(".m4a"):
            mime_type = "audio/mp4"
        elif filename.endswith(".ogg") or filename.endswith(".webm"):
            mime_type = "audio/ogg"

        files = {
            "file": (filename, audio_bytes, mime_type)
        }
        data = {
            "model": "saaras:v4",
            "language_code": language_code
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(SARVAM_STT_URL, headers=headers, data=data, files=files)
        except Exception as exc:
            logger.error("Failed to call Sarvam speech-to-text: %s", exc)
            raise SarvamAPIError(f"Speech-to-text service error: {str(exc)}")

        if not res.is_success:
            raise SarvamAPIError(f"Sarvam Speech-to-Text failed (HTTP {res.status_code}): {res.text}", status_code=res.status_code)

        result_data = res.json()
        return result_data.get("transcript", "").strip()

    async def synthesize_speech(
        self,
        text: str,
        language_code: str = "hi-IN",
        speaker: str = "meera"
    ) -> Optional[str]:
        """
        Synthesizes text to speech using Sarvam Bulbul model.
        Returns base64 encoded audio string.
        """
        key = self.api_key
        if not key:
            raise SarvamConfigurationError("SARVAM_API_KEY is not configured for text-to-speech.")

        # Cap text length to avoid token limits
        clean_text = text[:1000].strip()
        if not clean_text:
            return None

        headers = {
            "api-subscription-key": key,
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": [clean_text],
            "target_language_code": language_code,
            "speaker": speaker,
            "model": "bulbul:v4-flash",
            "speech_sample_rate": 24000,
            "audio_format": "mp3"
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(SARVAM_TTS_URL, headers=headers, json=payload)
        except Exception as exc:
            logger.error("Failed to call Sarvam text-to-speech: %s", exc)
            raise SarvamAPIError(f"Text-to-speech service error: {str(exc)}")

        if not res.is_success:
            raise SarvamAPIError(f"Sarvam Text-to-Speech failed (HTTP {res.status_code}): {res.text}", status_code=res.status_code)

        result_data = res.json()
        audios = result_data.get("audios", [])
        return audios[0] if audios else None

sarvam_service_instance = SarvamAIService()

