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
    job_id = Column(Integer, nullable=True)
    cv_file_path = Column(String(500), nullable=False)
    cv_text = Column(Text, nullable=True)
    report_file_path = Column(String(500), nullable=False)
    report_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
