from backend.core.logging import logger
from backend.models.schemas import (
    InterviewQuestionRequest,
    InterviewQuestionResponse,
    InterviewQuestion,
    DifficultyLevel
)
from ai.chains import extraction_chains


class InterviewQuestionGenerator:
    """
    Service for generating interview questions based on resume, job description, and missing skills.
    """

    def __init__(self):
        self.extraction_chains = extraction_chains
        logger.info("InterviewQuestionGenerator initialized")

    def generate_questions(self, request: InterviewQuestionRequest) -> InterviewQuestionResponse:
        """
        Generate interview questions.

        Args:
            request: InterviewQuestionRequest with candidate data

        Returns:
            InterviewQuestionResponse with generated questions
        """
        try:
            logger.info("Generating interview questions")

            # Set default difficulty distribution if not provided
            difficulty_distribution = request.difficulty_distribution or {
                "Easy": 2,
                "Medium": 2,
                "Hard": 1
            }

            # Generate questions using LLM chain
            question_dicts = self.extraction_chains.generate_interview_questions(
                candidate_name=request.candidate_name or "Candidate",
                resume_data=request.structured_resume.dict(),
                jd_data=request.structured_job_description.dict(),
                missing_skills=request.missing_skills,
                difficulty_distribution=difficulty_distribution
            )

            # Convert dicts to InterviewQuestion objects
            questions = []
            for q_dict in question_dicts:
                # Ensure difficulty is a valid DifficultyLevel
                difficulty = q_dict.get("difficulty", "Medium")
                if difficulty not in [level.value for level in DifficultyLevel]:
                    difficulty = "Medium"

                questions.append(InterviewQuestion(
                    question=q_dict.get("question", ""),
                    difficulty=DifficultyLevel(difficulty),
                    category=q_dict.get("category", "General"),
                    context=q_dict.get("context")
                ))

            # Create response
            response = InterviewQuestionResponse(
                candidate_name=request.candidate_name,
                total_questions=len(questions),
                questions=questions
            )

            logger.info(f"Successfully generated {len(questions)} interview questions")
            return response

        except Exception as e:
            logger.error(f"Error generating interview questions: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate interview questions: {str(e)}")


# Singleton instance
interview_question_generator = InterviewQuestionGenerator()
