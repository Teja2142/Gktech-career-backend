from sqlalchemy import Column, String, Text, DateTime
from .database import Base
import uuid
from datetime import datetime


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False)
    phone = Column(String(50), nullable=False)
    linkedin = Column(String(255))
    role = Column(String(100))
    work_auth_status = Column(String(100))
    preferred_location = Column(String(100))
    availability = Column(String(100))
    comments = Column(Text)
    resume_url = Column(String(1024))
    origin_domain = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


