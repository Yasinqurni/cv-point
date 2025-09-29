import tempfile
import uuid
import os
from abc import ABC, abstractmethod
from fastapi import UploadFile
import aio_pika
from fastapi import Depends
from sqlalchemy.orm import Session
import json
import requests
import re

from app.entity.models.queue_model import QueueSource, QueueStatus
from app.entity.requests.create_candidate_request import CreateCandidateRequest
from app.entity.responses.evaluate_candidate_response import EvaluateCandidateResponse
from app.pkg.db import get_db
from app.pkg.cloudinary import upload_document
from app.pkg.llm import get_llm_client
from app.pkg.rag import query_rag
from app.pkg.text_extractor import extract_text_from_file
from app.services.job_service import JobService
from ..repositories.candidate_repository import CandidateRepository, get_candidate_repository, CandidateRepositoryImpl
from ..repositories.queue_repository import QueueRepository, get_queue_repository, QueueRepositoryImpl
from app.pkg.rabbitmq import ExchangeName, QueueName, publish_message
from app.entity.responses.create_candidate_response import CreateCandidateResponse
from app.entity.responses.result_candidate_response import ResultCandidateResponse, ResultCandidate
from ..repositories.result_repository import ResultRepository, get_result_repository, ResultRepositoryImpl
from ..repositories.job_repository import JobRepository, get_job_repository, JobRepositoryImpl


class CandidateService(ABC):
    @abstractmethod
    async def handle_upload(self, req: CreateCandidateRequest) -> CreateCandidateResponse:
        ...

    @abstractmethod
    async def evaluate(self, id: int) -> EvaluateCandidateResponse:
        ...

    @abstractmethod
    def process_data_upload(self, message: any):
        ...

    @abstractmethod
    async def result(self, id: any) -> ResultCandidateResponse:
        ...


class CandidateServiceImpl(CandidateService):
    def __init__(
        self, 
        candidateRepository: CandidateRepository,
        queueRepository: QueueRepository,
        resultRepository: ResultRepository,
        jobRepository: JobRepository,
        db: Session,
    ):
        self.candidateRepository = candidateRepository
        self.queueRepository = queueRepository
        self.resultRepository = resultRepository
        self.jobRepository = jobRepository
        self.db = db

    async def handle_upload(self, req: CreateCandidateRequest) -> CreateCandidateResponse:
        cv_suffix = os.path.splitext(req.cv.filename)[-1]
        cv_tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{cv_suffix}")
        with open(cv_tmp_path, "wb") as buffer:
            buffer.write(await req.cv.read())

        report_suffix = os.path.splitext(req.project_report.filename)[-1]
        report_tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{report_suffix}")
        with open(report_tmp_path, "wb") as buffer:
            buffer.write(await req.project_report.read())

        cv_upload = upload_document(cv_tmp_path, f"candidates/{req.cv.filename}")
        report_upload = upload_document(report_tmp_path, f"candidates/{req.project_report.filename}")

        if os.path.exists(cv_tmp_path):
            os.remove(cv_tmp_path)
        
        if os.path.exists(report_tmp_path):
            os.remove(report_tmp_path)

        cv_file_url = cv_upload['secure_url']
        report_file_url = report_upload['secure_url']
        
        candidate = self.candidateRepository.create(req.candidate_name, cv_file_url, report_file_url, req.job_id)

        return CreateCandidateResponse(id=candidate.id)

    async def evaluate(self, id: int) -> EvaluateCandidateResponse:
        candidate = self.candidateRepository.get_by_id(id)
        if not candidate:
            raise ValueError("Candidate not found")
        
        queue = self.queueRepository.get_by_source_and_upload_id(QueueSource.CANDIDATE.value, candidate.id)
        if queue:
            return EvaluateCandidateResponse(id=candidate.id, status=queue.status)

        cv_url = candidate.cv_file_url
        report_url = candidate.report_file_url

        cv_suffix = os.path.splitext(cv_url)[-1] or ".pdf"
        report_suffix = os.path.splitext(report_url)[-1] or ".pdf"
        cv_tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{cv_suffix}")
        report_tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{report_suffix}")

        with requests.get(cv_url, stream=True) as r:
            r.raise_for_status()
            with open(cv_tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with requests.get(report_url, stream=True) as r:
            r.raise_for_status()
            with open(report_tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        cv_text = extract_text_from_file(cv_tmp_path)
        report_text = extract_text_from_file(report_tmp_path)

        if os.path.exists(cv_tmp_path):
            os.remove(cv_tmp_path)
        if os.path.exists(report_tmp_path):
            os.remove(report_tmp_path)

        queue = self.queueRepository.create(candidate.id, QueueSource.CANDIDATE.value)
        publish_data = {
            "candidate_id": candidate.id,
            "job_id": candidate.job_id,
            "queue_id": queue.id,
            "cv_text": cv_text,
            "report_text": report_text
        }

        try:
            publish_message(
                ExchangeName.CANDIDATE,
                QueueName.UPLOAD_CANDIDATE.value,
                json.dumps(publish_data).encode('utf-8')
            )
        except Exception as e:
            self.queueRepository.update_status_trx(queue.id, QueueStatus.FAILED.value, reason=str(e))
            raise e

        return EvaluateCandidateResponse(
            id=candidate.id,
            status=queue.status
        )

    def process_data_upload(self, message: any):
        try:
            data = json.loads(message.body.decode())
            queue_id = data.get("queue_id")
            cv_text = data.get("cv_text")
            report_text = data.get("report_text")
            candidate_id = data.get("candidate_id")
            job_id = data.get("job_id")

            if not queue_id or not candidate_id or not job_id:
                raise ValueError("Invalid message format")

            candidate = self.candidateRepository.get_by_id(candidate_id)
            if not candidate:
                raise ValueError("Candidate not found")

            job = self.jobRepository.get_by_id(job_id)
            if not job:
                raise ValueError("Job not found")

            llm = get_llm_client()
            prompt = (
                "You are an expert recruiter. Evaluate the following candidate's CV and project report "
                "against the given job requirements. Respond strictly in JSON format with the following fields:\n"
                '{\n'
                '  "cv_match_rate": number (0-100, how well the CV matches the job requirements),\n'
                '  "cv_feedback": string (detailed feedback about the candidate\'s CV),\n'
                '  "project_score": number (0-100, score for the project report),\n'
                '  "project_feedback": string (detailed feedback about the project report),\n'
                '  "overall_summary": string (overall assessment of the candidate)\n'
                '}\n\n'
                f"Job requirements context:\n{job.requirements}\n\n"
                f"Job description context:\n{job.description}\n\n"
                f"CV Text:\n{cv_text}\n\n"
                f"Project Report Text:\n{report_text}\n\n"
                "Return only valid JSON without any additional text."
)

            response = llm.generate_content(prompt)
            if not response.text or not response.text.strip():
                raise ValueError("LLM response is empty")

            match = re.search(r'\{.*?\}', response.text, re.DOTALL)
            if not match:
                raise ValueError("No JSON found in LLM response")

            result = json.loads(match.group(0))
            cv_match_rate = float(result.get("cv_match_rate", 0))
            cv_feedback = result.get("cv_feedback", "")
            project_score = float(result.get("project_score", 0))
            project_feedback = result.get("project_feedback", "")
            overall_summary = result.get("overall_summary", "")

            with self.db.begin():
                self.queueRepository.update_status_trx(queue_id, QueueStatus.COMPLETED.value)
                self.resultRepository.create(
                    queue_id=queue_id,
                    cv_match_rate=cv_match_rate,
                    cv_feedback=cv_feedback,
                    project_score=project_score,
                    project_feedback=project_feedback,
                    overall_summary=overall_summary,
                    raw_output=result
                )
            return True

        except Exception as e:
            self.queueRepository.update_status_trx(queue_id, QueueStatus.FAILED.value, reason=str(e))
            raise e

    async def result(self, id: int) -> ResultCandidateResponse:
        queue = self.queueRepository.get_by_id(id)
        if not queue:
            raise ValueError("Queue not found")
        
        if queue.source != QueueSource.JOB.value:
            raise ValueError("Queue source is not candidate")

        result = self.resultRepository.get_by_queue_id(id)
        if not result:
            raise ValueError("Result not found for this queue")
        
        resultData = ResultCandidate(
            cv_match_rate=result.cv_match_rate,
            cv_feedback=result.cv_feedback,
            project_score=result.project_score,
            project_feedback=result.project_feedback,
            overall_summary=result.overall_summary,
            raw_output=result.raw_output
        )
        return ResultCandidateResponse(
            queue_id=queue.id,
            status=queue.status,
            result=resultData
        )


def get_candidate_service(
    candidateRepository: CandidateRepositoryImpl = Depends(get_candidate_repository),
    queueRepository: QueueRepositoryImpl = Depends(get_queue_repository),
    resultRepository: ResultRepositoryImpl = Depends(get_result_repository),
    jobRepository: JobRepositoryImpl = Depends(get_job_repository),
    db: Session = Depends(get_db)
) -> CandidateService:
    return CandidateServiceImpl(candidateRepository, queueRepository, resultRepository, jobRepository, db)