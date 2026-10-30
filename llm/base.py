"""
Abstract Base LLM Provider.
Defines standard interface for model invocations, token tracking, and structured output.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'gemini', 'openai', 'mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Specific model identifier (e.g. 'gemini-2.5-flash')."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version string of the model."""
        pass

    @abstractmethod
    def extract_scheme_fields(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        prompt_version: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extracts structured scheme fields from document text.
        Returns:
            (extracted_fields_dict, execution_metadata_dict)
            execution_metadata_dict includes:
                input_tokens, output_tokens, total_tokens,
                latency_seconds, cost_usd, cost_status
        """
        pass
