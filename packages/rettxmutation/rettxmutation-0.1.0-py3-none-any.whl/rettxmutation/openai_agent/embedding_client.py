"""
Embedding Client

Handles text embeddings using Azure OpenAI's embedding API.
"""

import logging
import backoff
from typing import List
from openai import RateLimitError

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EmbeddingClient(BaseAgent):
    """Client for generating text embeddings using Azure OpenAI."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the embedding client."""
        super().__init__(*args, **kwargs)
        logger.debug(f"Embedding client initialized with deployment: {self._embedding_deployment}")

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError),
        max_tries=5
    )
    def create_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for a single text using Azure OpenAI's embedding API.
        
        Args:
            text: The text to embed
            
        Returns:
            List[float]: A list of floats representing the embedding vector
        """
        try:
            logger.debug(f"Creating embedding for text of length: {len(text)}")
            
            response = self.client.embeddings.create(
                model=self._embedding_deployment,
                input=text,
                encoding_format="float"
            )

            # Extract the embedding vector from the response
            embedding_vector = response.data[0].embedding
            
            logger.debug(f"Created embedding vector of dimension: {len(embedding_vector)}")
            
            return embedding_vector
            
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single request.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            logger.debug(f"Creating embeddings for {len(texts)} texts")
            
            response = self.client.embeddings.create(
                model=self._embedding_deployment,
                input=texts,
                encoding_format="float"
            )

            # Extract embedding vectors from the response
            embedding_vectors = [item.embedding for item in response.data]
            
            logger.debug(f"Created {len(embedding_vectors)} embedding vectors")
            
            return embedding_vectors
            
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise
