import os
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import faiss
from backend.core.logging import logger
from backend.utils.embedding_utils import embedding_generator


def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    """
    Normalize vectors to unit length (L2 normalization).
    This is required for using Inner Product to be equivalent to cosine similarity.
    
    Args:
        vectors: Numpy array of shape (n_vectors, embedding_dim)
    
    Returns:
        Normalized vectors of the same shape
    """
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    # Avoid division by zero for zero vectors
    norms[norms == 0] = 1
    return vectors / norms


class FAISSVectorStore:
    """
    FAISS-based vector store for storing and searching embeddings.
    Uses cosine similarity via normalized vectors and IndexFlatIP.
    Supports storing document embeddings along with metadata.
    """

    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.index = None
        self.metadata = []  # List to store metadata for each embedding
        self.embedding_dim = None
        
        # Ensure index directory exists
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing index
        self._load_index()
        
        logger.info(f"FAISSVectorStore initialized at {index_path}")

    def _load_index(self):
        """Load FAISS index and metadata from disk if they exist."""
        try:
            if (self.index_path / "index.faiss").exists() and (self.index_path / "metadata.pkl").exists():
                self.index = faiss.read_index(str(self.index_path / "index.faiss"))
                with open(self.index_path / "metadata.pkl", "rb") as f:
                    self.metadata = pickle.load(f)
                self.embedding_dim = self.index.d
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.warning(f"Failed to load existing index: {str(e)}")
            self.index = None
            self.metadata = []

    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path / "index.faiss"))
                with open(self.index_path / "metadata.pkl", "wb") as f:
                    pickle.dump(self.metadata, f)
                logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}", exc_info=True)
            raise Exception(f"Failed to save index: {str(e)}")

    def _initialize_index(self, embedding_dim: int):
        """Initialize a new FAISS index with the given embedding dimension."""
        # Use IndexFlatIP for Inner Product (equivalent to cosine similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.embedding_dim = embedding_dim
        logger.info(f"Initialized new FAISS index with dimension {embedding_dim} (cosine similarity)")

    def add_embeddings(self, texts: List[str], metadatas: List[Dict]):
        """
        Add embeddings and metadata to the index.

        Args:
            texts: List of text strings to embed and add
            metadatas: List of metadata dictionaries (one per text)
        """
        if len(texts) != len(metadatas):
            raise ValueError("Number of texts must match number of metadatas")

        # Generate embeddings
        embeddings = embedding_generator.generate_embeddings(texts)
        
        # Normalize embeddings for cosine similarity
        normalized_embeddings = normalize_vectors(embeddings)
        
        # Initialize index if needed
        if self.index is None:
            self._initialize_index(normalized_embeddings.shape[1])
        elif normalized_embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {normalized_embeddings.shape[1]}")

        # Add embeddings to index
        self.index.add(normalized_embeddings.astype(np.float32))
        
        # Add metadata
        self.metadata.extend(metadatas)
        
        # Save index
        self._save_index()
        
        logger.info(f"Added {len(texts)} embeddings to the index")

    def search(self, query_text: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search the index for the most similar vectors to the query using cosine similarity.

        Args:
            query_text: Query text string
            k: Number of top results to return

        Returns:
            List of tuples (metadata, cosine_similarity), sorted by similarity (highest first)
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty, no results to return")
            return []

        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query_text).reshape(1, -1).astype(np.float32)
        
        # Normalize query embedding
        normalized_query = normalize_vectors(query_embedding)
        
        # Search index (returns inner product, which is cosine similarity for normalized vectors)
        similarities, indices = self.index.search(normalized_query, k)
        
        # Prepare results
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:  # -1 means no result found for that position
                results.append((self.metadata[idx], float(similarities[0][i])))
        
        logger.info(f"Search returned {len(results)} results for query")
        return results

    def clear(self):
        """Clear the index and metadata."""
        self.index = None
        self.metadata = []
        self.embedding_dim = None
        
        # Delete index files if they exist
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"
        
        if index_file.exists():
            index_file.unlink()
        if metadata_file.exists():
            metadata_file.unlink()
        
        logger.info("Cleared FAISS index")


# Initialize vector stores for resumes and job descriptions
data_dir = Path("data")
resume_vector_store = FAISSVectorStore(data_dir / "faiss_index" / "resumes")
jd_vector_store = FAISSVectorStore(data_dir / "faiss_index" / "job_descriptions")
