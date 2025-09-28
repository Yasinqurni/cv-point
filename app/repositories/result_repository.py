from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from app.entity.models.result_model import Result
from fastapi import Depends
from pkg.db import get_db


class ResultRepository(ABC):
    @abstractmethod
    def create(
        self,
        job_id: int,
        cv_match_rate: float,
        cv_feedback: str,
        project_score: float,
        project_feedback: str,
        overall_summary: str,
        raw_output: dict
    ) -> Result:
        ...
    
    @abstractmethod
    def get_by_job_id(self, job_id: int) -> Optional[Result]:
        ...


class ResultRepositoryImpl(ResultRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        job_id: int,
        cv_match_rate: float,
        cv_feedback: str,
        project_score: float,
        project_feedback: str,
        overall_summary: str,
        raw_output: dict
    ) -> Result:
        result = Result(
            job_id=job_id,
            cv_match_rate=cv_match_rate,
            cv_feedback=cv_feedback,
            project_score=project_score,
            project_feedback=project_feedback,
            overall_summary=overall_summary,
            raw_output=raw_output
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_by_job_id(self, job_id: int) -> Result | None:
        return self.db.query(Result).filter(Result.job_id == job_id).first()


def get_result_repository(
    db: Session = Depends(get_db),
) -> ResultRepository:
    return ResultRepositoryImpl(db)