from sqlalchemy import Column, Integer, String, Text
from .database import Base
import uuid


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False)
    phone = Column(String(15), nullable=False)
    linkedin = Column(String(255))
    role = Column(String(100))
    work_auth_status = Column(String(100))
    preferred_location = Column(String(100))
    availability = Column(String(100))
    comments = Column(Text)
    resume_url = Column(String(512))
    created_at = Column(String(50), nullable=False, default="CURRENT_TIMESTAMP")
    updated_at = Column(String(50), nullable=False, default="CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


