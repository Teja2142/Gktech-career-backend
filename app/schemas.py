from pydantic import BaseModel, EmailStr
from typing import Optional

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
