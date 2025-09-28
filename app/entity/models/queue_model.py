from sqlalchemy import (
    Column, Integer, String, Text, Float, Enum, JSON,
    ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import relationship, declarative_base
import enum

db = declarative_base()

class QueueSource(str, enum.Enum):
    JOB = "jobs"
    CANDIDATE = "candidates"

class QueueStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Queue(db):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(Integer, nullable=False)  # bisa job_id atau candidate_id
    source = Column(Enum("jobs", "candidates", native_enum=False), nullable=False)
    status = Column(Enum("queued", "processing", "completed", "failed", native_enum=False), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
