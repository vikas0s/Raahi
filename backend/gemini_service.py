"""
Gemini AI Integration Service for Raahi.
Provides fast, multilingual, and reliable communication with Google Gemini:
- Uses Google Gemini REST API (gemini-3.5-flash-lite / gemini-flash-latest)
- Pure Hindi (हिंदी), natural Hinglish, and professional English responses
- asyncio.to_thread with urllib.request for resilient, zero-timeout execution on Windows
"""
import os
import json
import logging
import asyncio
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

root_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=root_env)
load_dotenv()

logger = logging.getLogger("raahi.gemini")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_GEMINI_MODELS = ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-3.8-flash"]
DEFAULT_TIMEOUT_SEC = 14.0

class GeminiConfigurationError(Exception):
    """Raised when GEMINI_API_KEY is missing or invalid."""
    pass

class GeminiAPIError(Exception):
    """Raised when the Gemini API returns an HTTP error or malformed response."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

def _sync_gemini_call(url: str, payload_bytes: bytes, timeout: float) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))

class GeminiAIService:
    def __init__(self):
        self._default_model = DEFAULT_GEMINI_MODEL

    @property
    def api_key(self) -> str:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        return key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        """
        Calls Gemini generateContent REST API with conversation history.
        Translates standard role-based messages into Gemini's contents schema.
        """
        key = self.api_key
        if not key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not configured in backend environment (.env)."
            )

        target_model = model or os.getenv("GEMINI_MODEL", self._default_model)

        # Separate system prompt if present in messages
        extracted_sys = system_instruction
        gemini_contents = []

        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                if not extracted_sys:
                    extracted_sys = content
                else:
                    extracted_sys += f"\n\n{content}"
            elif role in ("assistant", "model"):
                gemini_contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
            else:
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })

        if not gemini_contents:
            gemini_contents.append({
                "role": "user",
                "parts": [{"text": "Hello"}]
            })

        payload: Dict[str, Any] = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if extracted_sys:
            payload["system_instruction"] = {
                "parts": [{"text": extracted_sys}]
            }

        payload_bytes = json.dumps(payload).encode("utf-8")

        # Models list with fallback chain
        models_to_try = [target_model]
        for fb in FALLBACK_GEMINI_MODELS:
            if fb not in models_to_try:
                models_to_try.append(fb)

        last_error = None
        for current_model in models_to_try:
            url = f"{GEMINI_BASE_URL}/{current_model}:generateContent?key={key}"
            try:
                data = await asyncio.to_thread(_sync_gemini_call, url, payload_bytes, DEFAULT_TIMEOUT_SEC)
                candidates = data.get("candidates", [])
                if not candidates:
                    raise GeminiAPIError("Gemini API response contained no candidates.", status_code=200)
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts or not parts[0].get("text"):
                    raise GeminiAPIError("Gemini candidate contained no text parts.", status_code=200)
                return parts[0]["text"].strip()
            except urllib.error.HTTPError as http_err:
                err_text = http_err.read().decode("utf-8", errors="ignore")
                logger.warning("Gemini model %s returned HTTP %s: %s", current_model, http_err.code, err_text[:160])
                if http_err.code == 404:
                    continue  # Try next fallback model
                last_error = GeminiAPIError(f"Gemini API returned HTTP {http_err.code}: {err_text}", status_code=http_err.code)
                break
            except Exception as exc:
                logger.warning("Gemini model %s call failed: %s", current_model, exc)
                last_error = GeminiAPIError(f"Gemini API error on {current_model}: {exc}", status_code=500)
                continue

        if last_error:
            raise last_error
        raise GeminiAPIError("Failed to obtain response from Gemini API.", status_code=500)

gemini_service_instance = GeminiAIService()
