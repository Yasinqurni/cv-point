# CV-Point Backend Service

A backend service for automated job and candidate evaluation using FastAPI, LLM (Gemini), RAG, RabbitMQ, and MySQL.

## Features

- Job document upload, text extraction, and queue-based processing
- Candidate CV & project report upload, evaluation, and result retrieval
- Asynchronous processing with RabbitMQ
- LLM & RAG integration for intelligent extraction and evaluation
- Modular, clean architecture

## Project Structure

```
app/
  controllers/      # API controllers for job and candidate
  entity/           # Models, requests, responses
  pkg/              # Utilities: LLM, RAG, RabbitMQ, Cloudinary, etc.
  repositories/     # Data access layer for job, candidate, queue, result
  routers/          # API endpoint routing
  services/         # Business logic for job and candidate
migrations/         # Database migration scripts
requirements.txt    # Python dependencies
Dockerfile
docker-compose.yaml
README.md
```

## Prerequisites

- Docker & Docker Compose installed
- (Optional) .env file for environment variables

## Running with Docker

1. **Build and start all services (API, RabbitMQ, MySQL, migration):**
   ```sh
   docker-compose up --build
   ```

   This will:
   - Build the FastAPI app image
   - Start RabbitMQ (with management UI at http://localhost:15672)
   - Start MySQL (port 3306)
   - Run database migrations automatically using dbmate

2. **Access the API:**
   - FastAPI runs at: [http://localhost:8000](http://localhost:8000)
   - RabbitMQ UI: [http://localhost:15672](http://localhost:15672) (user: guest, pass: guest)
   - MySQL: `localhost:3306` (user: cvuser, pass: cvpass, db: cvpoint)

3. **(Optional) Run only migrations:**
   ```sh
   docker-compose run --rm migrate
   ```

## API Endpoints (Main)

- `POST /jobs/upload` — Upload a job document
- `GET /jobs` — List jobs
- `POST /candidates/upload` — Upload candidate CV & project report
- `POST /candidates/{id}/evaluate` — Trigger candidate evaluation
- `GET /candidates/{id}/result` — Get candidate evaluation result

## How It Works

1. User uploads job/candidate documents via API.
2. Files are saved, text is extracted, and data is sent to a queue.
3. Worker/consumer processes queue, runs LLM & RAG, and updates the database.
4. User can retrieve evaluation results via API.

## Migration

- All migration scripts are in the `migrations/` folder.
- Migrations are run automatically by the `migrate` service in Docker Compose using [dbmate](https://github.com/amacneil/dbmate).

## Technology Stack

- Python, FastAPI, SQLAlchemy
- RabbitMQ (queue)
- Google Gemini (LLM)
- FAISS (RAG)
- Cloudinary (file storage)
- MySQL (DB)
- dbmate (migration)

## Notes

- Make sure to configure your `.env` file if needed (for DB, Cloudinary, Gemini API key, etc).
- For development, you can use Docker volumes to persist data.

---

Feel free to adjust the endpoints, environment, or add more usage examples as needed!