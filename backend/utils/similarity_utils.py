import numpy as np
from typing import Union
from backend.core.logging import logger


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Cosine similarity measures the cosine of the angle between two vectors,
    which is a measure of how similar the vectors are regardless of their magnitude.
    
    Formula:
        cos_sim = (vec1 · vec2) / (||vec1|| * ||vec2||)
    
    Args:
        vec1: First vector (1D numpy array)
        vec2: Second vector (1D numpy array)
    
    Returns:
        Cosine similarity score between -1 and 1
        - 1 means vectors are identical
        - 0 means vectors are orthogonal
        - -1 means vectors are opposite
    """
    # Ensure vectors are numpy arrays
    vec1 = np.asarray(vec1).flatten()
    vec2 = np.asarray(vec2).flatten()
    
    # Check vector dimensions
    if vec1.shape != vec2.shape:
        raise ValueError(f"Vectors must have the same dimension. Got {vec1.shape} and {vec2.shape}")
    
    # Calculate dot product
    dot_product = np.dot(vec1, vec2)
    
    # Calculate norms
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = dot_product / (norm1 * norm2)
    
    return float(similarity)


def cosine_similarity_matrix(vectors1: np.ndarray, vectors2: np.ndarray = None) -> np.ndarray:
    """
    Calculate cosine similarity matrix between two sets of vectors.
    
    Args:
        vectors1: First set of vectors (shape: n_vectors1 x embedding_dim)
        vectors2: Second set of vectors (shape: n_vectors2 x embedding_dim).
                  If None, calculates similarity between vectors1 and itself.
    
    Returns:
        Cosine similarity matrix (shape: n_vectors1 x n_vectors2)
    """
    vectors1 = np.asarray(vectors1)
    
    # Normalize vectors
    norms1 = np.linalg.norm(vectors1, axis=1, keepdims=True)
    norms1[norms1 == 0] = 1
    normalized1 = vectors1 / norms1
    
    if vectors2 is None:
        vectors2 = vectors1
    
    vectors2 = np.asarray(vectors2)
    norms2 = np.linalg.norm(vectors2, axis=1, keepdims=True)
    norms2[norms2 == 0] = 1
    normalized2 = vectors2 / norms2
    
    # Calculate similarity matrix
    similarity_matrix = np.dot(normalized1, normalized2.T)
    
    return similarity_matrix
