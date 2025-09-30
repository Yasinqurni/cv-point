from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy.orm import Session
from app.entity.models.candidate_model import Candidate
from fastapi import Depends
from app.pkg.db import get_db


class CandidateRepository(ABC): 
    @abstractmethod
    def create(self, candidate_name: str, cv_file_path: str, report_file_path: str, job_id: int, cv_text: str, report_text: str) -> Candidate:
        ...
    
    @abstractmethod
    def get_by_id(self, upload_id: int) -> Optional[Candidate]:
        ...
    
    @abstractmethod
    def list_all(self) -> List[Candidate]:
        ...


class CandidateRepositoryImpl(CandidateRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, candidate_name: str, cv_file_path: str, report_file_path: str, job_id: int, cv_text: str, report_text: str) -> Candidate:
        candidate = Candidate(
            candidate_name=candidate_name,
            cv_file_path=cv_file_path,
            report_file_path=report_file_path,
            job_id=job_id,
            cv_text=cv_text,
            report_text=report_text
        )
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def get_by_id(self, upload_id: int) -> Candidate | None:
        return self.db.query(Candidate).filter(Candidate.id == upload_id).first()

    def list_all(self) -> list[Candidate]:
        return self.db.query(Candidate).all()


def get_candidate_repository(
    db: Session = Depends(get_db),
) -> CandidateRepository:
    return CandidateRepositoryImpl(db)