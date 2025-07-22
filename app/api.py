# app/api.py

from fastapi import FastAPI, UploadFile, File, Form, Depends, Request, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, s3_utils
from .database import SessionLocal, engine
from .models import Submission
from .schemas import SubmissionResponse, SubmissionRequest
from typing import List,Optional

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Router for all endpoints
router = APIRouter()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/submit",
    summary="Submit Career Form",
    tags=["Submission"],
    response_model=SubmissionResponse,
    responses={
        400: {
            "description": "Invalid file type",
            "content": {
                "application/json": {
                    "example": {"detail": "Resume must be a PDF or DOCX file."}
                }
            },
        },
        500: {
            "description": "Submission failed or internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Submission failed",
                        "error": "Error details here"
                    }
                }
            },
        },
    },
)
async def submit_form(
    full_name: str = Form(..., description="Full name", example="Jane Doe"),
    email: str = Form(..., description="Email", example="jane@example.com"),
    phone: str = Form(..., description="Phone number", example="+91-9876543210"),
    linkedin: Optional[str] = Form(None, description="LinkedIn URL", example="https://linkedin.com/in/janedoe"),
    role: str = Form(..., description="Role applying for", example="Backend Developer"),
    work_auth_status: str = Form(..., description="Work auth status", example="Citizen"),
    preferred_location: str = Form(..., description="Preferred location", example="Hyderabad"),
    availability: str = Form(..., description="Availability", example="Immediate"),
    comments: Optional[str] = Form(None, description="Comments", example="Open to remote"),
    resume: UploadFile = File(..., description="Resume file (PDF/DOCX)"),
    db: Session = Depends(get_db)
):
    """
    Submit a career form along with a resume file. The resume will be uploaded to AWS S3.
    """
    try:
        # Optional: Validate resume file type
        if not resume.filename.lower().endswith((".pdf", ".docx")):
            return JSONResponse(
                status_code=400,
                content={"detail": "Resume must be a PDF or DOCX file."},
            )

        # Upload file to S3
        resume_url = s3_utils.upload_resume_to_s3(resume.file, resume.filename)

        # Save submission to DB
        import uuid
        submission = Submission(
            id=str(uuid.uuid4()),
            full_name=full_name,
            email=email,
            phone=phone,
            linkedin=linkedin,
            role=role,
            work_auth_status=work_auth_status,
            preferred_location=preferred_location,
            availability=availability,
            comments=comments,
            resume_url=resume_url,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        return SubmissionResponse(
            id=submission.id,
            resume_url=resume_url,
        )

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Submission failed",
                "error": str(exc),
            },
        )

def create_app() -> FastAPI:
    app = FastAPI(
        title="Career Submission API",
        description="Submit resumes with form data and upload to AWS S3.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Enable CORS (allow all for dev; restrict in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "error": str(exc),
            },
        )

    app.include_router(router)
    return app

# Create FastAPI app instance
app = create_app()
