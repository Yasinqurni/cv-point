from sqlalchemy.orm import Session
from app.entity.models import job_model as Job

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, upload_id: int, status: str = "queued") -> Job:
        job = Job(upload_id=upload_id, status=status)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_status(self, job_id: int, status: str) -> Job | None:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            self.db.commit()
            self.db.refresh(job)
        return job

    def get_by_id(self, job_id: int) -> Job | None:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def list_by_upload(self, upload_id: int) -> list[Job]:
        return self.db.query(Job).filter(Job.upload_id == upload_id).all()
