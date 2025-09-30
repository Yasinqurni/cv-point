from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from app.entity.models.result_model import Result
from fastapi import Depends
from app.pkg.db import get_db


class ResultRepository(ABC):
    @abstractmethod
    def create_trx(
        self,
        queue_id: int,
        cv_match_rate: float,
        cv_feedback: str,
        project_score: float,
        project_feedback: str,
        overall_summary: str,
        raw_output: dict
    ) -> Result:
        ...
    
    @abstractmethod
    def get_by_queue_id(self, queue_id: int) -> Optional[Result]:
        ...


class ResultRepositoryImpl(ResultRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_trx(
        self,
        queue_id: int,
        cv_match_rate: float,
        cv_feedback: str,
        project_score: float,
        project_feedback: str,
        overall_summary: str,
        raw_output: dict
    ) -> Result:
        result = Result(
            queue_id=queue_id,
            cv_match_rate=cv_match_rate,
            cv_feedback=cv_feedback,
            project_score=project_score,
            project_feedback=project_feedback,
            overall_summary=overall_summary,
            raw_output=raw_output
        )
        self.db.add(result)
        self.db.flush()
        return result

    def get_by_queue_id(self, queue_id: int) -> Result | None:
        return self.db.query(Result).filter(Result.queue_id == queue_id).first()


def get_result_repository(
    db: Session = Depends(get_db),
) -> ResultRepository:
    return ResultRepositoryImpl(db)