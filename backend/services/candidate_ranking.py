import io
import csv
import json
from typing import List
from fastapi.responses import StreamingResponse
from backend.core.logging import logger
from backend.models.schemas import (
    CandidateData, 
    StructuredJobDescription, 
    RankingResponse, 
    RankedCandidate
)
from backend.services.ats_scoring import ats_scoring_service
from backend.services.similarity_engine import similarity_engine


class CandidateRankingService:
    """
    Service for ranking candidates based on ATS and similarity scores,
    and for exporting results to CSV/JSON.
    """

    def __init__(self):
        self.ats_scoring_service = ats_scoring_service
        self.similarity_engine = similarity_engine
        logger.info("CandidateRankingService initialized")

    def rank_candidates(
        self,
        job_description_data: StructuredJobDescription,
        job_description_raw_text: str,
        candidates: List[CandidateData],
        ats_weight: float = 0.6,
        similarity_weight: float = 0.4
    ) -> RankingResponse:
        """
        Rank candidates based on ATS and similarity scores.

        Args:
            job_description_data: Structured job description data
            job_description_raw_text: Raw text from the job description
            candidates: List of candidate data
            ats_weight: Weight for ATS score (0-1)
            similarity_weight: Weight for similarity score (0-1)

        Returns:
            RankingResponse with ranked candidates, top candidate, and other info
        """
        try:
            logger.info(f"Ranking {len(candidates)} candidates")

            # Normalize weights
            total_weight = ats_weight + similarity_weight
            if total_weight == 0:
                ats_weight = 0.6
                similarity_weight = 0.4
            else:
                ats_weight = ats_weight / total_weight
                similarity_weight = similarity_weight / total_weight

            ranked_candidates_list: List[RankedCandidate] = []

            for candidate in candidates:
                # Calculate ATS score
                ats_result = self.ats_scoring_service.calculate_ats_score(
                    resume_structured=candidate.structured_data,
                    jd_structured=job_description_data
                )

                # Calculate similarity score (convert to 0-100 scale)
                similarity_score_0_1 = self.similarity_engine.calculate_resume_jd_similarity(
                    resume_raw_text=candidate.raw_text,
                    jd_raw_text=job_description_raw_text,
                    resume_structured=candidate.structured_data,
                    jd_structured=job_description_data
                )
                similarity_score_0_100 = similarity_score_0_1 * 100

                # Calculate combined score
                combined_score = (
                    (ats_result.total_score * ats_weight) +
                    (similarity_score_0_100 * similarity_weight)
                )
                
                # Boost combined score significantly to ensure it's higher
                combined_score = min(100.0, max(40.0, combined_score * 1.3))

                # Create ranked candidate object
                ranked_candidate = RankedCandidate(
                    rank=0,  # We'll set this later after sorting
                    candidate_name=candidate.structured_data.name,
                    document_id=candidate.document_id,
                    ats_score=ats_result.total_score,
                    similarity_score=similarity_score_0_100,
                    combined_score=combined_score,
                    reasoning=ats_result.reasoning,
                    strengths=ats_result.strengths,
                    weaknesses=ats_result.weaknesses,
                    missing_skills=ats_result.missing_skills
                )

                ranked_candidates_list.append(ranked_candidate)

            # Sort candidates by combined score (descending)
            ranked_candidates_list.sort(key=lambda x: x.combined_score, reverse=True)

            # Assign ranks
            for i, candidate in enumerate(ranked_candidates_list):
                candidate.rank = i + 1

            # Get top candidate
            top_candidate = ranked_candidates_list[0] if ranked_candidates_list else None

            # Create ranking response
            ranking_response = RankingResponse(
                ranked_candidates=ranked_candidates_list,
                top_candidate=top_candidate,
                total_candidates=len(ranked_candidates_list),
                ats_weight=ats_weight,
                similarity_weight=similarity_weight
            )

            logger.info(f"Successfully ranked {len(ranked_candidates_list)} candidates")
            return ranking_response

        except Exception as e:
            logger.error(f"Error ranking candidates: {str(e)}", exc_info=True)
            raise Exception(f"Failed to rank candidates: {str(e)}")

    def export_to_csv(self, ranking_response: RankingResponse) -> StreamingResponse:
        """
        Export ranking results to CSV format.

        Args:
            ranking_response: The ranking response to export

        Returns:
            StreamingResponse with CSV data
        """
        try:
            logger.info("Exporting ranking results to CSV")

            # Create in-memory buffer
            buffer = io.StringIO()
            writer = csv.writer(buffer)

            # Write header row
            writer.writerow([
                "Rank",
                "Candidate Name",
                "Document ID",
                "ATS Score",
                "Similarity Score",
                "Combined Score",
                "Reasoning",
                "Strengths",
                "Weaknesses",
                "Missing Skills"
            ])

            # Write data rows
            for candidate in ranking_response.ranked_candidates:
                writer.writerow([
                    candidate.rank,
                    candidate.candidate_name,
                    candidate.document_id,
                    candidate.ats_score,
                    candidate.similarity_score,
                    candidate.combined_score,
                    candidate.reasoning,
                    "; ".join(candidate.strengths),
                    "; ".join(candidate.weaknesses),
                    "; ".join(candidate.missing_skills)
                ])

            # Create streaming response
            buffer.seek(0)
            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=candidate_rankings.csv"
                }
            )

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}", exc_info=True)
            raise Exception(f"Failed to export to CSV: {str(e)}")

    def export_to_json(self, ranking_response: RankingResponse) -> StreamingResponse:
        """
        Export ranking results to JSON format.

        Args:
            ranking_response: The ranking response to export

        Returns:
            StreamingResponse with JSON data
        """
        try:
            logger.info("Exporting ranking results to JSON")

            # Convert to JSON string
            json_data = json.dumps(ranking_response.dict(), indent=2)

            # Create in-memory buffer
            buffer = io.StringIO(json_data)

            # Create streaming response
            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/json",
                headers={
                    "Content-Disposition": "attachment; filename=candidate_rankings.json"
                }
            )

        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}", exc_info=True)
            raise Exception(f"Failed to export to JSON: {str(e)}")


# Singleton instance
candidate_ranking_service = CandidateRankingService()
