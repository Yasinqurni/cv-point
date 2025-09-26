from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum, JSON,
    ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import relationship, declarative_base

db = declarative_base()

class Result(db):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    cv_match_rate = Column(Float, nullable=True)
    cv_feedback = Column(Text, nullable=True)
    project_score = Column(Float, nullable=True)
    project_feedback = Column(Text, nullable=True)
    overall_summary = Column(Text, nullable=True)
    raw_output = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # relationships
    job = relationship("Job", back_populates="result")
