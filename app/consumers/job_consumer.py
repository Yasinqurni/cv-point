from app.services.job_service import JobServiceImpl
from app.pkg.db import get_db
from app.repositories.queue_repository import QueueRepositoryImpl
from app.repositories.job_repository import JobRepositoryImpl

async def process_job_queue(message):
    db = get_db()
    queueRepository = QueueRepositoryImpl(db)
    jobRepository = JobRepositoryImpl(db)
    job_service = JobServiceImpl(queueRepository=queueRepository, db=db, jobRepository=jobRepository)

    try:
        await job_service.process_data_upload(message)
    except Exception as e:
        print(f"Error processing job: {e}")
