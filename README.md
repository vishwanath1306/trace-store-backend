# LLM Trace Storage Backend

A backend service for storing, processing, and semantically searching log traces using vector embeddings.


```bash
uv venv .venv
source .venv/bin/activate

uv pip install -r requirements.txt
```

Example configuration:
```yaml
DevelopmentConfig:
  DEBUG: true
  SQLALCHEMY_DATABASE_URI: "postgresql://postgres:postgres@localhost/trace_store_db"
  SQLALCHEMY_TRACK_MODIFICATIONS: false
  CELERY_BROKER_URL: "redis://localhost:6379/0"
  CELERY_RESULT_BACKEND: "redis://localhost:6379/1"
  OPENAI_KEY: "your-openai-key"
  GCP_API_key: "your-gcp-key"
  GCP_MODEL_NAME: "text-bison@001"
  JOBS_STORAGE:
    HOST: "localhost"
    PORT: 6379
    DB: 2
  MILVUS_HOST: "localhost"
  MILVUS_PORT: 19530
```

### Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
sudo -u postgres psql

CREATE DATABASE trace_store_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE trace_store_db TO postgres;

\c trace_store_db

CREATE EXTENSION IF NOT EXISTS vector;

\q
```

### Initialize and Run Database Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
```

Add this import at the top of the migration (because of a bug with alembic or flask-migrate)

```py
import pgvector.sqlalchemy
```


```bash
flask db upgrade
```

### Start Redis Server

Make sure Redis is running:

```bash
redis-server
```

### Start Milvus (optional)

Follow the [Milvus installation guide](https://milvus.io/docs/install_standalone-docker.md) to set up Milvus using Docker:

```bash
# Example Docker command for Milvus
docker run -d --name milvus_standalone -p 19530:19530 -p 19121:19121 milvusdb/milvus:latest
```

### Start Celery Worker

```bash
celery --app=tasks.task:celery worker --loglevel=INFO
```

### Run the Flask Application

```bash
python app.py
```

### Run the Inference app (placeholder)

```bash
python inference_server/app.py
```

The application will be available at http://localhost:5000

## API Endpoints

Check staging.txt for sample commands

- `GET /api/v1/session/session-hw` - Health check endpoint

```bash
curl http://localhost:5000/api/v1/session/session-hw
```

- `POST /api/v1/session/create` - Create a new session

```bash
curl -X POST http://localhost:5000/api/v1/session/create \
-F "session_name=test_session" \
-F "vector_database=Postgres" \
-F "embedding_method=GOOGLE" \
-F "application_name=openstack" \
-F "request_file=@/path/to/your/logfile.log"
```

- `GET /api/v1/session/details` - Get session details

```bash
curl http://localhost:5000/api/v1/session/details?session_id=your_session_id
```

- `GET /api/v1/session/current-status` - Get current status

```bash
curl http://localhost:5000/api/v1/session/current-status?session_id=your_session_id
```

- `GET /api/v1/session/get-all-sessions` - Get all sessions

```bash
curl http://localhost:5000/api/v1/session/get-all-sessions
```

- `POST /api/v1/session/query-logs` - Query logs using semantic search

```bash
curl -X POST http://localhost:5000/api/v1/session/query-logs \
-H "Content-Type: application/json" \
-d '{
"session_id": "your_session_id",
"query_string": "error in authentication"
}'
```


## Project Structure

- `app.py` - Main application entry point
- `init.py` - Flask application initialization
- `config.py` - Configuration loading
- `models/` - Database models
- `modules/` - Application modules and routes
- `services/` - External service integrations (Redis, Milvus, OpenAI)
- `tasks/` - Celery background tasks
- `utils/` - Utility functions and helpers
- `migrations/` - Database migrations