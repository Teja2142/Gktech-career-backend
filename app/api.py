from typing import Optional
from urllib.parse import urlparse
import uuid
from fastapi import FastAPI, UploadFile, File, Form, Depends, Request, APIRouter, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from . import s3_utils, models
from .database import SessionLocal, engine
from .models import Submission
from .schemas import SubmissionResponse
from .email_service import email_service
from fastapi.middleware.cors import CORSMiddleware
import io

# Create DB tables
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

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
)
async def submit_form(
    request: Request,
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    linkedin: Optional[str] = Form(None),
    role: str = Form(...),
    work_auth_status: str = Form(...),
    preferred_location: str = Form(...),
    availability: str = Form(...),
    comments: Optional[str] = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        if not resume.filename.lower().endswith((".pdf", ".docx")):
            raise HTTPException(status_code=400, detail="Resume must be a PDF or DOCX file.")

        origin = request.headers.get("origin") or request.headers.get("referer")
        if not origin:
            host = request.headers.get("x-forwarded-host") or request.headers.get("host")
            if host:
                origin = f"http://{host}"
        if not origin:
            raise HTTPException(status_code=400, detail="Unable to determine request origin or host.")

        print(f"Request origin: {origin}")

        domain = urlparse(origin).hostname
        if domain and domain.startswith("www."):
            domain = domain[4:]

        print(f"Extracted domain: {domain}")

        file_bytes = await resume.read()


        # Upload to S3 using BytesIO (so we can reuse the same bytes)
        resume_url = s3_utils.upload_resume_to_s3(io.BytesIO(file_bytes), resume.filename)

        # Save submission
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
            origin_domain=domain,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # Get recipient email for response (resolve via service)
        recipient_email = email_service.get_recipient(domain)

        # Schedule email sending in background
        background_tasks.add_task(email_service.send_email, submission, resume.filename, file_bytes)

        return SubmissionResponse(id=submission.id, resume_url=resume_url, sent_to_email=recipient_email)

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


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
    return HTTPException(
        status_code=500,
        detail="Internal Server Error",
    )

app.include_router(router)


