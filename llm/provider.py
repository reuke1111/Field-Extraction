"""
LLM Provider implementations and factory.
Supports Google Gemini, OpenAI-compatible APIs, and Mock Provider.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Tuple, Optional
from config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    LLM_MODEL_NAME,
    INPUT_TOKEN_PRICE_PER_M,
    OUTPUT_TOKEN_PRICE_PER_M
)
from llm.base import BaseLLMProvider
from llm.mock_provider import MockLLMProvider
from llm.prompts import SYSTEM_EXTRACTION_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self._model_name = model_name
        self._model_version = "2026-v2.5"
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize google.genai client: {e}")
            self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return self._model_version

    def extract_scheme_fields(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        prompt_version: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if not self._client:
            raise RuntimeError("Gemini client not initialized. Check GEMINI_API_KEY.")

        start_time = time.time()
        user_prompt = build_user_prompt(document_text, document_metadata)

        # Call with retry on malformed JSON
        max_retries = 2
        last_error = None
        response_text = ""
        input_tokens = 0
        output_tokens = 0

        for attempt in range(max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=user_prompt,
                    config={
                        "system_instruction": SYSTEM_EXTRACTION_PROMPT,
                        "temperature": 0.0,
                        "response_mime_type": "application/json"
                    }
                )
                response_text = response.text or ""
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                    output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                else:
                    input_tokens = len(user_prompt) // 4
                    output_tokens = len(response_text) // 4

                # Clean markdown blocks if present
                clean_json = response_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()

                parsed = json.loads(clean_json)
                latency = time.time() - start_time

                # Calculate cost
                cost = (input_tokens / 1_000_000) * INPUT_TOKEN_PRICE_PER_M + (output_tokens / 1_000_000) * OUTPUT_TOKEN_PRICE_PER_M

                metadata = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "latency_seconds": round(latency, 4),
                    "estimated_cost_usd": round(cost, 6),
                    "cost_status": "calculated",
                    "provider": self.provider_name,
                    "model_name": self.model_name,
                    "model_version": self.model_version
                }
                return parsed, metadata

            except Exception as e:
                last_error = e
                time.sleep(1.0)

        raise RuntimeError(f"Gemini extraction failed after {max_retries} retries: {last_error}")


def get_llm_provider(
    provider_override: Optional[str] = None,
    api_key_override: Optional[str] = None
) -> BaseLLMProvider:
    """
    Factory creating configured LLM provider.
    Defaults to MockLLMProvider if no valid credentials exist or 'mock' is requested.
    """
    provider_choice = (provider_override or LLM_PROVIDER).lower()

    if provider_choice == "gemini":
        key = api_key_override or GEMINI_API_KEY
        if key and key.strip():
            return GeminiLLMProvider(api_key=key, model_name=LLM_MODEL_NAME)
        else:
            logger.info("GEMINI_API_KEY not configured. Falling back to MockLLMProvider.")
            return MockLLMProvider()

    # Default to deterministic mock provider
    return MockLLMProvider()
