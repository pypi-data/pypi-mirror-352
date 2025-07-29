from typing import List, Optional

from ...application.agents.base_embedding_service import BaseEmbeddingService
from ...domain.agents.interfaces.llm_embedding_repository import LlmEmbeddingRepository
from ...infrastructure.agents.ollama.factories import OllamaFactory


class EmbeddingService(BaseEmbeddingService):
    """
    Implementation of an embedding service that can work with any embedding model.
    """

    def __init__(self, api_url: str, api_token: str = None, model_name: str = None):
        """
        Initialize a new EmbeddingService.

        Args:
            api_url: The base URL of the API.
            api_token: Optional API token for authentication.
            model_name: The name of the model to use.

        Raises:
            ValueError: If the api_url is empty or None, or if the model_name is invalid.
        """
        super().__init__(api_url, api_token)

        if not model_name:
            raise ValueError("Model name cannot be empty or None")

        self.model_name = model_name

        # Create factory based on model name
        if OllamaFactory.is_embedding_model(model_name):
            self.factory = OllamaFactory(
                api_url=api_url,
                api_token=api_token,
                model_name=model_name
            )
        else:
            raise ValueError(f"Unsupported embedding model: {model_name}")

        # Create repository
        self.embedding_repository: LlmEmbeddingRepository = self.factory.create_embedding_repository()

        if self.embedding_repository is None:
            raise ValueError(f"Model {model_name} does not support embeddings")

    def embed(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for the given text.

        Args:
            text: The text to create an embedding for.

        Returns:
            Optional[List[float]]: The embedding vector, or None if an error occurs.

        Raises:
            ValueError: If the text is empty or None.
        """
        if not text:
            raise ValueError("Text cannot be empty or None")

        return self.embedding_repository.embed(text)

    def batch_embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Create embeddings for multiple texts in a single batch.

        Args:
            texts: List of texts to create embeddings for.

        Returns:
            Optional[List[List[float]]]: List of embedding vectors, or None if an error occurs.

        Raises:
            ValueError: If the text list is empty or None.
        """
        if not texts:
            raise ValueError("Texts list cannot be empty or None")

        # Filter out empty texts
        valid_texts = [text for text in texts if text]
        if not valid_texts:
            raise ValueError("All texts in the list are empty")

        # Process each text individually
        # If the repository supports batch processing, this could be optimized
        embeddings = []
        for text in valid_texts:
            embedding = self.embed(text)
            if embedding is None:
                return None  # If any embedding fails, return None
            embeddings.append(embedding)

        return embeddings
