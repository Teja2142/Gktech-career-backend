from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    linkedin = Column(String)
    role = Column(String)
    work_auth_status = Column(String)
    preferred_location = Column(String)
    availability = Column(String)
    comments = Column(Text)
    resume_url = Column(String)
