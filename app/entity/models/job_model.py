from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum, JSON,
    ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import relationship, declarative_base

db = declarative_base()



class Job(db):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("queued", "processing", "completed", "failed", name="job_status"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # relationships
    upload = relationship("Upload", back_populates="jobs")
    result = relationship("Result", back_populates="job", uselist=False, cascade="all, delete-orphan")
