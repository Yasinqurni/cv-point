from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy.orm import Session
from app.entity.models.queue_model import Queue, QueueStatus
from fastapi import Depends
from app.pkg.db import get_db


class QueueRepository(ABC):
    @abstractmethod
    def create_trx(self, upload_id: int, source: str, status: str = QueueStatus.QUEUED.value) -> Queue:
        ...
    
    @abstractmethod
    def update_status(self, queue_id: int, status: str) -> Optional[Queue]:
        ...
    
    @abstractmethod
    def get_by_id(self, queue_id: int) -> Optional[Queue]:
        ...
    
    @abstractmethod
    def list_by_upload(self, upload_id: int) -> List[Queue]:
        ...


class QueueRepositoryImpl(QueueRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_trx(self, upload_id: int, source: str, status: str = QueueStatus.QUEUED.value) -> Queue:
        queue = Queue(upload_id=upload_id, source=source, status=status)
        self.db.add(queue)
        self.db.flush()
        return queue

    def update_status(self, queue_id: int, status: str) -> Queue | None:
        queue = self.db.query(Queue).filter(Queue.id == queue_id).first()
        if queue:
            queue.status = status
            self.db.commit()
            self.db.refresh(queue)
        return queue

    def get_by_id(self, queue_id: int) -> Queue | None:
        return self.db.query(Queue).filter(Queue.id == queue_id).first()

    def list_by_upload(self, upload_id: int) -> list[Queue]:
        return self.db.query(Queue).filter(Queue.upload_id == upload_id).all()


def get_queue_repository(
    db: Session = Depends(get_db),
) -> QueueRepository:
    return QueueRepositoryImpl(db)
