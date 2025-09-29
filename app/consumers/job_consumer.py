
import asyncio
from email import message
import json
from app.pkg.rabbitmq import consume_queue, QueueName
from app.pkg.llm import get_llm_client
from app.pkg.db import get_db
from app.repositories.job_repository import JobRepositoryImpl
from app.repositories.queue_repository import QueueRepositoryImpl
from app.entity.models.queue_model import QueueStatus
from app.pkg.rag import query_rag

async def process_job_queue(message):
    try:
        db = next(get_db())
        job_repo = JobRepositoryImpl(db)
        queue_repo = QueueRepositoryImpl(db)

        # Decode message
        try:
            data = json.loads(message.body.decode())
        except Exception as e:
            print(f"Error decoding message body: {e}")
            return

        queue_id = data.get("queue_id")
        text = data.get("data")

        if not queue_id or not text:
            print("Invalid message format, skipping")
            return

        rag_context = query_rag(text, top_k=3)

        llm = get_llm_client()
        prompt = (
            "Ekstrak title, deskripsi, dan requirement dari teks berikut. "
            "Jawab hanya dalam format JSON seperti contoh berikut: "
            '{"title": "...", "description": "...", "requirement": "..."}\n\n'
            f"Context referensi:\n{rag_context}\n\nTeks:\n{text}"
        )

        try:
            response = llm.generate_content(prompt)
            if not response.text or not response.text.strip():
                print("LLM response is empty")
                result = {}
            else:
                import re
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                else:
                    print(f"No JSON found in LLM response: {response.text}")
                    result = {}
        except Exception as e:
            print(f"Error generating or parsing LLM content: {e}")
            result = {}

        title = result.get("title", "")
        description = result.get("description", "")
        requirements = result.get("requirement", "")
        with db.begin():
            try:
                job = job_repo.update_trx(queue_id, title, description, requirements)
                if job is None:
                    print(f"Job with id {queue_id} not found")
                    queue_repo.update_status_trx(queue_id, QueueStatus.FAILED.value)
                    return

                queue_repo.update_status_trx(queue_id, QueueStatus.COMPLETED.value)
                db.refresh(job)
            except Exception as e:
                db.rollback()
                queue_repo.update_status_trx(queue_id, QueueStatus.FAILED.value)
                print(f"Error updating job or queue status: {e}")

    except Exception as e:
        print(f"Error processing job: {e}")
