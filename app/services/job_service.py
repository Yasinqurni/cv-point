import tempfile
import uuid
import os
from abc import ABC, abstractmethod
from fastapi import UploadFile
import aio_pika
from fastapi import Depends
from sqlalchemy.orm import Session
import json
import re

from app.entity.models.queue_model import QueueSource, QueueStatus
from app.pkg.db import get_db
from app.pkg.cloudinary import upload_document
from app.pkg.llm import get_llm_client
from app.pkg.rag import query_rag
from app.pkg.text_extractor import extract_text_from_file
from ..repositories.job_repository import JobRepository, get_job_repository, JobRepositoryImpl
from ..repositories.queue_repository import QueueRepository, get_queue_repository, QueueRepositoryImpl
from app.pkg.rabbitmq import ExchangeName, QueueName, publish_message
from app.entity.responses.create_job_response import CreateJobResponse
from app.entity.responses.get_list_job_response import GetListJobResponse


class JobService(ABC):
    @abstractmethod
    async def handle_upload(self, file: UploadFile) -> CreateJobResponse:
        ...

    @abstractmethod
    async def get_list(self) -> list[GetListJobResponse]:
        ...
    
    @abstractmethod
    async def process_data_upload(self, message: any):
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

    async def handle_upload(self, file: UploadFile) -> CreateJobResponse:
        suffix = os.path.splitext(file.filename)[-1]
        tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
        with open(tmp_path, "wb") as buffer:
            buffer.write(await file.read())

        text = extract_text_from_file(tmp_path)

        data_upload = upload_document(tmp_path, f"jobs/{file.filename}")

        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        file_url = data_upload['secure_url']
        with self.db.begin():
            job = self.jobRepository.create_trx(file_url)
            queue = self.queueRepository.create_trx(job.id, QueueSource.JOB.value)

            self.db.refresh(job)

        publish_data = {"queue_id": queue.id, "data": text}

        try:
            publish_message(
                ExchangeName.JOB,
                QueueName.UPLOAD_JOB.value,
                json.dumps(publish_data).encode('utf-8')
            )
        except Exception as e:
            self.queueRepository.update_status_trx(queue.id, QueueStatus.FAILED.value, reason=str(e))
            raise e

        return CreateJobResponse(id=job.id, file_url=file_url, status=queue.status)
    
    async def get_list(self) -> list[GetListJobResponse]:
        jobs = self.jobRepository.get_list()
        response = [GetListJobResponse(id=job.id, title=job.title) for job in jobs]

        return response
    
    def process_data_upload(self, message: any):
        try:
            # 1. Decode message
            data = json.loads(message.body.decode())
            queue_id = data.get("queue_id")
            text = data.get("data")

            queue = self.queueRepository.get_by_id(queue_id)
            if not queue:
                raise ValueError(f"Queue with id {queue_id} not found")

            if not queue_id or not text:
                raise ValueError("Invalid message format")

            # 2. Query RAG context
            rag_context = query_rag(text, top_k=3)

            # 3. Build prompt & call LLM
            llm = get_llm_client()
            
            prompt = (
                "Extract the title, description, and requirements from the following text. "
                "Respond only in JSON format as in this example: "
                '{"title": "...", "description": "...", "requirement": "..."}\n\n'
                f"Reference context:\n{rag_context}\n\nText:\n{text}"
            )

            response = llm.generate_content(prompt)
            if not response.text or not response.text.strip():
                raise ValueError("LLM response is empty")

            match = re.search(r'\{.*?\}', response.text, re.DOTALL)
            if not match:
                raise ValueError("No JSON found in LLM response")

            result = json.loads(match.group(0))

            title = result.get("title", "")
            description = result.get("description", "")
            requirements = result.get("requirement") or result.get("requirements") or ""

            # 4. DB Transaction
            with self.db.begin():
                job = self.jobRepository.update_trx(queue_id, title, description, requirements)
                if job is None:
                    raise ValueError(f"Job with id {queue_id} not found")

                self.queueRepository.update_status_trx(queue_id, QueueStatus.COMPLETED.value)
                self.db.refresh(job)

            return True

        except Exception as e:
            self.queueRepository.update_status_trx(queue_id, QueueStatus.FAILED.value, reason=str(e))
       
            raise e



def get_job_service(
    jobRepository:  JobRepositoryImpl = Depends(get_job_repository),
    queueRepository: QueueRepositoryImpl = Depends(get_queue_repository),
    db: Session = Depends(get_db)
) -> JobService:
    return JobServiceImpl(jobRepository, queueRepository, db)