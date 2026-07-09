import numpy as np
import os
import shutil
from pathlib import Path
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
from backend.core.config import settings
from backend.core.logging import logger


class EmbeddingGenerator:
    """
    Class for generating embeddings using Sentence Transformers.
    Uses all-MiniLM-L6-v2 as the default model.
    """

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.model = None
        logger.info(f"EmbeddingGenerator initialized with model: {self.model_name}")
        self._load_model()  # Load model right away on initialization

    def _clear_model_cache(self):
        """Clear both system and project-specific Hugging Face caches to ensure fresh download."""
        cache_dirs = [
            Path.home() / ".cache" / "huggingface" / "hub",  # System-wide cache
            Path(__file__).parent.parent.parent / "data" / "huggingface_cache"  # Project-specific cache
        ]
        
        for cache_dir in cache_dirs:
            try:
                if cache_dir.exists():
                    logger.info(f"Clearing cache directory: {cache_dir}")
                    # Delete all items in the cache directory
                    for item in cache_dir.iterdir():
                        try:
                            if item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                            else:
                                item.unlink(missing_ok=True)
                        except Exception as e:
                            logger.warning(f"Failed to delete cache item {item}: {e}")
            except Exception as e:
                logger.warning(f"Failed to clear cache directory {cache_dir}: {str(e)}", exc_info=True)

    def _load_model(self):
        """Load the Sentence Transformers model with cache corruption handling."""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Loading Sentence Transformer model: {self.model_name} (attempt {attempt + 1}/{max_retries})")
                self.model = SentenceTransformer(
                    self.model_name,
                    trust_remote_code=True
                )
                logger.info("Model loaded successfully")
                return
            except Exception as e:
                logger.error(f"Failed to load model (attempt {attempt + 1}): {str(e)}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info("Clearing model cache and trying again...")
                    self._clear_model_cache()
                    self.model = None  # Reset model to try again
                else:
                    logger.warning(f"Failed to load SentenceTransformer model. Will use fallback similarity method.")
                    self.model = None  # Mark model as failed to load
                    return

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            Numpy array of the embedding
        """
        self._load_model()
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate embedding: {str(e)}")

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text strings.

        Args:
            texts: List of input texts to embed

        Returns:
            Numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        self._load_model()
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate embeddings: {str(e)}")


# Singleton instance
embedding_generator = EmbeddingGenerator()
