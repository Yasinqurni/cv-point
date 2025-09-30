from app.services.candidate_service import CandidateServiceImpl
from app.pkg.db import get_db_session
from app.repositories.queue_repository import QueueRepositoryImpl
from app.repositories.job_repository import JobRepositoryImpl
from app.repositories.result_repository import ResultRepositoryImpl
from app.repositories.candidate_repository import CandidateRepositoryImpl

async def process_candidate_queue(message):
    db = get_db_session()
    queueRepository = QueueRepositoryImpl(db)
    jobRepository = JobRepositoryImpl(db)
    resultRepository = ResultRepositoryImpl(db)
    candidateRepository = CandidateRepositoryImpl(db)
    candidate_service = CandidateServiceImpl(
        queueRepository=queueRepository, 
        db=db, 
        jobRepository=jobRepository,
        resultRepository=resultRepository,
        candidateRepository=candidateRepository,
        )

    try:
        await candidate_service.process_data_upload(message)
    except Exception as e:
        print(f"Error processing candidate: {e}")
