from fastapi import APIRouter, HTTPException
from backend.models.schemas import InterviewQuestionRequest, InterviewQuestionResponse, ErrorResponse
from backend.services.interview_question_generator import interview_question_generator
from backend.core.logging import logger

router = APIRouter(prefix="/interview-questions", tags=["interview-questions"])


@router.post("/generate", response_model=InterviewQuestionResponse, responses={400: {"model": ErrorResponse}})
async def generate_interview_questions(request: InterviewQuestionRequest):
    """
    Generate 5 interview questions based on the candidate's resume, job description, and missing skills.
    Questions cover Missing Skills, Experience, and Projects with Easy, Medium, and Hard difficulty levels.
    """
    try:
        logger.info("Received interview question generation request")
        response = interview_question_generator.generate_questions(request)
        return response
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
