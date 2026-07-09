from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from backend.core.config import settings
from backend.core.logging import logger
from backend.api.v1 import resume, job, embeddings, similarity, ats, ranking, interview_questions, hiresense

app = FastAPI(title="HireSense AI - Resume Screening API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
Path("data/temp").mkdir(parents=True, exist_ok=True)

# Include API routers
app.include_router(resume.router, prefix="/api/v1")
app.include_router(job.router, prefix="/api/v1")
app.include_router(embeddings.router, prefix="/api/v1")
app.include_router(similarity.router, prefix="/api/v1")
app.include_router(ats.router, prefix="/api/v1")
app.include_router(ranking.router, prefix="/api/v1")
app.include_router(interview_questions.router, prefix="/api/v1")
app.include_router(hiresense.router, prefix="/api/v1")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "HireSense AI API is running!",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
