from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SubmissionCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    linkedin: Optional[str] = None
    role: str
    work_auth_status: str
    preferred_location: str
    availability: str
    comments: Optional[str] = None


class SubmissionRequest(BaseModel):
    full_name: str = Field(..., description="Full name", example="Jane Doe")
    email: str = Field(..., description="Email", example="jane@example.com")
    phone: str = Field(..., description="Phone number", example="+91-9876543210")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL", example="https://linkedin.com/in/janedoe")
    role: str = Field(..., description="Role applying for", example="Backend Developer")
    work_auth_status: str = Field(..., description="Work authorization status", example="Citizen")
    preferred_location: str = Field(..., description="Preferred job location", example="Hyderabad")
    availability: str = Field(..., description="Availability to join", example="Immediate")
    comments: Optional[str] = Field(None, description="Additional comments", example="Open to remote or hybrid roles")
    # resume should be handled as UploadFile in the endpoint, not inside Pydantic model


class SubmissionResponse(BaseModel):
    id: str
    resume_url: str
    sent_to_email: Optional[str] = None

    model_config = {"from_attributes": True}


class ContactRequest(BaseModel):
    full_name: str
    company: Optional[str] = None
    inquiry_type: Optional[str] = None
    email: Optional[EmailStr] = None
    message: Optional[str] = None


class ContactResponse(BaseModel):
    id: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}

