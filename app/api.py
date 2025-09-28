from typing import Optional
from urllib.parse import urlparse
import uuid
import time
import logging
from fastapi import FastAPI, UploadFile, File, Form, Depends, Request, APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import s3_utils, models
import os
from .database import SessionLocal, engine
from .models import Submission,Contact
from .schemas import SubmissionResponse
from .email_service import email_service
from fastapi.middleware.cors import CORSMiddleware
import io

# Create DB tables
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

# basic logger for timing
logger = logging.getLogger("career")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

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

        origin = get_request_origin(request)
        domain = urlparse(origin).hostname or ""
        if domain.startswith("www."):
            domain = domain[4:]

        if domain:
            print(f"Extracted domain: {domain}")

        start_total = time.time()

        file_bytes = await resume.read()

        # Upload resume bytes to MinIO and time it
        start_upload = time.time()
        resume_url = s3_utils.upload_resume_to_minio(file_bytes, resume.filename)
        upload_duration = time.time() - start_upload
        logger.info(f"MinIO upload completed in {upload_duration:.3f}s for file={resume.filename}")

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

        # Save submission and time DB operation
        start_db = time.time()
        db.add(submission)
        db.commit()
        db.refresh(submission)
        db_duration = time.time() - start_db
        logger.info(f"DB save completed in {db_duration:.3f}s for submission_id={submission.id}")

        # Get recipient email for response (resolve via service). If none, fall back to CONTACT_RECEIVER or SMTP_USER
        recipient_email = email_service.get_recipient(domain) or os.getenv("CONTACT_RECEIVER") or os.getenv("SMTP_USER")

        # Schedule email sending in background (pass domain if needed)
        background_tasks.add_task(email_service.send_email, submission, resume.filename, file_bytes)
        logger.info("Email send scheduled in background")

        total_duration = time.time() - start_total
        logger.info(f"Total /submit request handled in {total_duration:.3f}s for submission_id={submission.id}")

        return SubmissionResponse(id=submission.id, resume_url=resume_url, sent_to_email=recipient_email)

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))






@router.post("/contact", summary="Contact form", tags=["Contact"])
async def contact_form(
    request: Request,
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    company: Optional[str] = Form(None),
    inquiry_type: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        # determine origin domain for contact
        origin = get_request_origin(request)
        domain = urlparse(origin).hostname or ""
        if domain.startswith("www."):
            domain = domain[4:]

        contact = Contact(
            id=str(uuid.uuid4()),
            full_name=full_name,
            company=company,
            inquiry_type=inquiry_type,
            email=email,
            message=message,
            origin_domain=domain
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        # send email in background (pass domain so receiver resolves correctly)
        background_tasks.add_task(email_service.send_contact_email, contact, domain)

        return JSONResponse(status_code=201, content={"id": contact.id})
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    




def get_request_origin(request: Request) -> str:
    origin = request.headers.get("origin") or request.headers.get("referer")
    if not origin:
        host = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if host:
            origin = f"http://{host}"
    if not origin:
        raise HTTPException(status_code=400, detail="Unable to determine request origin or host.")
    return origin





app = FastAPI(
    title="Career Submission API",
    description="Submit resumes with form data and upload to MinIO (local VM).",
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
