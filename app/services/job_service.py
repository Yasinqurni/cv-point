import tempfile
import uuid
import os
from abc import ABC, abstractmethod
from fastapi import UploadFile
import aio_pika
from fastapi import Depends
from sqlalchemy.orm import Session
import json

from app.entity.models.queue_model import QueueSource
from app.pkg.db import get_db
from app.pkg.cloudinary import upload_document
from app.pkg.text_extractor import extract_text_from_file
from ..repositories.job_repository import JobRepository, get_job_repository, JobRepositoryImpl
from ..repositories.queue_repository import QueueRepository, get_queue_repository, QueueRepositoryImpl
from app.pkg.rabbitmq import ExchangeName, QueueName, publish_message


class JobService(ABC):
    @abstractmethod
    async def handle_upload(self, file: UploadFile):
       ...


class JobServiceImpl(JobService):
    def __init__(
        self, 
        jobRepository: JobRepository,
        queueRepository: QueueRepository,
        db: Session,
    ):
        self.jobRepository = jobRepository
        self.queueRepository = queueRepository
        self.db = db

    async def handle_upload(self, file: UploadFile):
        suffix = os.path.splitext(file.filename)[-1]
        tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
        with open(tmp_path, "wb") as buffer:
            buffer.write(await file.read())

        text = extract_text_from_file(tmp_path)
        print(text)
        data_upload = upload_document(tmp_path, f"jobs/{file.filename}")
        file_url = data_upload['secure_url']
        print(file_url)
        print(QueueSource.JOB.value)
        with self.db.begin():
            job = self.jobRepository.create_trx(file_url)
            queue = self.queueRepository.create_trx(job.id, QueueSource.JOB.value)

            self.db.refresh(job)

     
        publish_data = {"queue_id": queue.id, "data": text}
        await publish_message(
            ExchangeName.JOB,
            QueueName.UPLOAD_JOB.value,
            json.dumps(publish_data).encode('utf-8')
        )
        
        return {"id": job.id, "file_url": file_url, "status": queue.status}

def get_job_service(
    jobRepository:  JobRepositoryImpl = Depends(get_job_repository),
    queueRepository: QueueRepositoryImpl = Depends(get_queue_repository),
    db: Session = Depends(get_db)
) -> JobService:
    return JobServiceImpl(jobRepository, queueRepository, db)