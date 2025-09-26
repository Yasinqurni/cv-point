# CV Point - Clean Architecture (FastAPI)

## Setup

1. Copy environment template:
```bash
cp env.template .env
```

2. Update `.env` file with your actual values:
   - Database credentials
   - Gemini API key
   - Cloudinary credentials
   - RabbitMQ settings

3. Install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Based on `app/pkg/config.py`, the following environment variables are required:

### App Configuration
- `APP_NAME`: Application name (default: cv-point)
- `ENVIRONMENT`: Environment (default: development)
- `DEBUG_MODE`: Debug mode (default: true)
- `APP_PORT`: Application port (default: 8000)
- `APP_HOST`: Application host (default: 0.0.0.0)

### Database Configuration
- `DB_NAME`: Database name (required)
- `DB_HOST`: Database host (required)
- `DB_PASSWORD`: Database password (required)
- `DB_PORT`: Database port (required)
- `DB_USER`: Database user (required)

### RabbitMQ Configuration
- `RABBITMQ_HOST`: RabbitMQ host (default: localhost)
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USER`: RabbitMQ user (default: guest)
- `RABBITMQ_PASSWORD`: RabbitMQ password (default: guest)

### Gemini AI Configuration
- `GEMINI_API_KEY`: Gemini API key (required)
- `GEMINI_MODEL`: Gemini model (required)

### Cloudinary Configuration
- `CLOUDINARY_CLOUD_NAME`: Cloudinary cloud name (required)
- `CLOUDINARY_API_KEY`: Cloudinary API key (required)
- `CLOUDINARY_API_SECRET`: Cloudinary API secret (required)

## Project Structure

```
app/
├── pkg/                 # Package utilities
│   ├── config.py        # Configuration management
│   ├── db.py           # Database connection
│   ├── cloudinary.py   # Cloudinary integration
│   ├── llm.py          # LLM integration
│   ├── rabbitmq.py     # RabbitMQ integration
│   └── rag.py          # RAG implementation
├── entity/             # Domain entities
│   ├── models/         # Data models
│   ├── requests/       # Request models
│   └── responses/      # Response models
├── repositories/       # Data access layer
├── services/           # Business logic layer
├── controllers/        # Request handling
├── routers/           # API routes
└── consumers/         # Message consumers
```

## Health Check

- GET `/health`
