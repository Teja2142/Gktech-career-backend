from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

class SubmissionCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    linkedin: Optional[str]
    role: str
    work_auth_status: str
    preferred_location: str
    availability: str
    comments: Optional[str]


class SubmissionRequest(BaseModel):
    full_name: str = Field(..., description="Full name", examples=["Jane Doe"])
    email: str = Field(..., description="Email", examples=["jane@example.com"])
    phone: str = Field(..., description="Phone number", examples=["+91-9876543210"])
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL", examples=["https://linkedin.com/in/janedoe"])
    role: str = Field(..., description="Role applying for", examples=["Backend Developer"])
    work_auth_status: str = Field(..., description="Work authorization status", examples=["Citizen"])
    preferred_location: str = Field(..., description="Preferred job location", examples=["Hyderabad"])
    availability: str = Field(..., description="Availability to join", examples=["Immediate"])
    comments: Optional[str] = Field(None, description="Additional comments", examples=["Open to remote or hybrid roles"])
    resume: UploadFile = Field(..., description="Resume file (PDF/DOCX)")

class SubmissionResponse(BaseModel):
    id: str
    resume_url: str

    model_config = {
        "from_attributes": True
    }
