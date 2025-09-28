from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from app.entity.models.job_model import Job
from fastapi import Depends
from app.pkg.db import get_db



class JobRepository(ABC):
    @abstractmethod
    def create_trx(self, file_path: str, title: str = "", description: str = "", requirements: str = "") -> Job:
        ...
    
    @abstractmethod
    def get_list(self) -> Optional[Job]:
        ...
    
class JobRepositoryImpl(JobRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_trx(self, file_path: str, title: str = "", description: str = "", requirements: str = "") -> Job:
        job = Job(
            title=title,
            file_path=file_path,
            description=description,
            requirements=requirements,
        )
        self.db.add(job)
        self.db.flush()
        return job

    def get_list(self) -> list[Job]:
        return self.db.query(Job).filter(Job.title != "").all()


def get_job_repository(
    db: Session = Depends(get_db),
) -> JobRepository:
    return JobRepositoryImpl(db)
