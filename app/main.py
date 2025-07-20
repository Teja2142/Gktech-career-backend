from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, s3_utils
from .database import SessionLocal, engine
from .models import Submission

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Career Submission API",
    description="API for submitting career forms and uploading resumes to S3.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit", summary="Submit career form", tags=["Submission"])
async def submit_form(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    linkedin: str = Form(None),
    role: str = Form(...),
    work_auth_status: str = Form(...),
    preferred_location: str = Form(...),
    availability: str = Form(...),
    comments: str = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit a career form and upload resume to S3.
    """
    # Upload resume to S3
    resume_url = s3_utils.upload_resume_to_s3(resume.file, resume.filename)

    # Save to DB
    submission = Submission(
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

    return {"message": "Submission successful", "resume_url": resume_url}
