from abc import abstractmethod
from typing import Optional

from .base_repository import BaseRepository


class LlmGenerateRepository(BaseRepository):
    """
    Repository for text generation with an LLM.
    """

    @abstractmethod
    def generate(self, user_prompt: str, system_prompt: str = None, max_tokens: int = None) -> Optional[str]:
        """
        Generate text using the LLM.

        Args:
            user_prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to use.
            max_tokens: Optional maximum number of tokens to generate.

        Returns:
            Optional[str]: The generated text, or None if the request failed.
        """
        ...