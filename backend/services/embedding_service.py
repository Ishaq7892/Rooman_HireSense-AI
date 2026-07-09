from typing import List, Dict, Tuple
from backend.core.logging import logger
from backend.utils.embedding_utils import embedding_generator
from backend.services.vector_store import resume_vector_store, jd_vector_store
from backend.models.schemas import StructuredResume, StructuredJobDescription


class EmbeddingService:
    """
    Service class for managing embeddings and vector store operations.
    Handles both resumes and job descriptions.
    """

    def __init__(self):
        self.resume_store = resume_vector_store
        self.jd_store = jd_vector_store
        logger.info("EmbeddingService initialized")

    def _prepare_text_for_embedding(self, text: str, structured_data: Dict = None) -> str:
        """
        Prepare text for embedding by combining raw text with structured data (if available).

        Args:
            text: Raw text from the document
            structured_data: Structured data extracted from the document

        Returns:
            Combined text string for embedding
        """
        combined_text = text
        
        if structured_data:
            # Add structured data to the embedding text for better semantic matching
            additional_parts = []
            
            if "skills" in structured_data and structured_data["skills"]:
                additional_parts.append("Skills: " + ", ".join(structured_data["skills"]))
            
            if "experience" in structured_data and structured_data["experience"]:
                exp_parts = []
                for exp in structured_data["experience"]:
                    exp_str = f"{exp.get('job_title', '')} at {exp.get('company', '')}"
                    if exp.get("description"):
                        exp_str += f" - {exp['description']}"
                    exp_parts.append(exp_str)
                additional_parts.append("Experience: " + "; ".join(exp_parts))
            
            if "education" in structured_data and structured_data["education"]:
                edu_parts = []
                for edu in structured_data["education"]:
                    edu_str = f"{edu.get('degree', '')} from {edu.get('school', '')}"
                    edu_parts.append(edu_str)
                additional_parts.append("Education: " + "; ".join(edu_parts))
            
            if "required_skills" in structured_data and structured_data["required_skills"]:
                additional_parts.append("Required Skills: " + ", ".join(structured_data["required_skills"]))
            
            if "preferred_skills" in structured_data and structured_data["preferred_skills"]:
                additional_parts.append("Preferred Skills: " + ", ".join(structured_data["preferred_skills"]))
            
            if "technologies" in structured_data and structured_data["technologies"]:
                additional_parts.append("Technologies: " + ", ".join(structured_data["technologies"]))
            
            if additional_parts:
                combined_text += "\n\n" + "\n".join(additional_parts)
        
        return combined_text

    def embed_resume(self, document_id: str, raw_text: str, structured_data: StructuredResume = None) -> None:
        """
        Generate embedding for a resume and add it to the vector store.
        If embedding fails, just logs a warning (ranking will use fallback method).

        Args:
            document_id: Unique identifier for the resume
            raw_text: Raw text from the resume
            structured_data: Structured data extracted from the resume (optional)
        """
        try:
            # Only try to embed if model is available
            if embedding_generator.model is not None:
                logger.info(f"Embedding resume {document_id}")
                
                # Prepare text for embedding
                if structured_data is not None:
                    if hasattr(structured_data, "dict"):
                        structured_dict = structured_data.dict()
                    elif isinstance(structured_data, dict):
                        structured_dict = structured_data
                    else:
                        structured_dict = None
                else:
                    structured_dict = None
                embedding_text = self._prepare_text_for_embedding(raw_text, structured_dict)
                
                # Prepare metadata
                metadata = {
                    "document_id": document_id,
                    "document_type": "resume",
                    "raw_text": raw_text,
                    "structured_data": structured_dict
                }
                
                # Add to vector store
                self.resume_store.add_embeddings([embedding_text], [metadata])
                logger.info(f"Successfully embedded resume {document_id}")
            else:
                logger.warning(f"Skipping embedding for resume {document_id} - model not available")
        except Exception as e:
            logger.error(f"Error embedding resume {document_id}: {str(e)}", exc_info=True)
            logger.warning(f"Continuing without embedding for resume {document_id}")

    def embed_job_description(self, document_id: str, raw_text: str, structured_data: StructuredJobDescription = None) -> None:
        """
        Generate embedding for a job description and add it to the vector store.
        If embedding fails, just logs a warning (ranking will use fallback method).

        Args:
            document_id: Unique identifier for the job description
            raw_text: Raw text from the job description
            structured_data: Structured data extracted from the job description (optional)
        """
        try:
            # Only try to embed if model is available
            if embedding_generator.model is not None:
                logger.info(f"Embedding job description {document_id}")
                
                # Prepare text for embedding
                if structured_data is not None:
                    if hasattr(structured_data, "dict"):
                        structured_dict = structured_data.dict()
                    elif isinstance(structured_data, dict):
                        structured_dict = structured_data
                    else:
                        structured_dict = None
                else:
                    structured_dict = None
                embedding_text = self._prepare_text_for_embedding(raw_text, structured_dict)
                
                # Prepare metadata
                metadata = {
                    "document_id": document_id,
                    "document_type": "job_description",
                    "raw_text": raw_text,
                    "structured_data": structured_dict
                }
                
                # Add to vector store
                self.jd_store.add_embeddings([embedding_text], [metadata])
                logger.info(f"Successfully embedded job description {document_id}")
            else:
                logger.warning(f"Skipping embedding for job description {document_id} - model not available")
        except Exception as e:
            logger.error(f"Error embedding job description {document_id}: {str(e)}", exc_info=True)
            logger.warning(f"Continuing without embedding for job description {document_id}")

    def search_similar_resumes(self, jd_document_id: str, raw_text: str, k: int = 10) -> List[Tuple[Dict, float]]:
        """
        Search for resumes similar to a job description.

        Args:
            jd_document_id: Unique identifier for the job description
            raw_text: Raw text from the job description
            k: Number of top results to return

        Returns:
            List of tuples (resume_metadata, distance), sorted by similarity (closest first)
        """
        try:
            logger.info(f"Searching for similar resumes for JD {jd_document_id}")
            
            # Get JD structured data if available
            jd_metadata = None
            for md in self.jd_store.metadata:
                if md.get("document_id") == jd_document_id:
                    jd_metadata = md
                    break
            
            # Prepare query text
            structured_dict = jd_metadata.get("structured_data") if jd_metadata else None
            query_text = self._prepare_text_for_embedding(raw_text, structured_dict)
            
            # Search resume store
            results = self.resume_store.search(query_text, k)
            logger.info(f"Found {len(results)} similar resumes")
            return results
        except Exception as e:
            logger.error(f"Error searching similar resumes: {str(e)}", exc_info=True)
            raise Exception(f"Failed to search similar resumes: {str(e)}")

    def clear_resume_store(self) -> None:
        """Clear all resumes from the vector store."""
        self.resume_store.clear()
        logger.info("Resume vector store cleared")

    def clear_jd_store(self) -> None:
        """Clear all job descriptions from the vector store."""
        self.jd_store.clear()
        logger.info("Job description vector store cleared")


# Singleton instance
embedding_service = EmbeddingService()
