from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum, JSON,
    ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import relationship, declarative_base

db = declarative_base()

class Candidate(db):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_name = Column(String(255), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    cv_file_path = Column(String(500), nullable=False)
    report_file_path = Column(String(500), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # relationships
    jobs = relationship("Job", back_populates="candidates")

