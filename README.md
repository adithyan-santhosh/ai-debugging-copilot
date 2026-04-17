# AI Debugging Copilot

A FastAPI backend prototype for ingesting logs, API traces, and DB queries, then using AI and RAG to surface root cause analysis, remediation guidance, and query optimization suggestions.

## Features

- Ingest logs, API trace JSON, and database query logs
- Detect slow queries, failed API calls, and application errors
- Summarize root cause and suggested fixes using OpenAI
- Provide query optimization hints and issue severity ranking
- Connects to PostgreSQL and MongoDB with async drivers

## Local setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

2. Copy the example env file and configure keys:

```bash
copy .env.example .env
```

3. Run the API server:

```bash
uvicorn app.main:app --reload
```

4. Use the endpoints:

- `POST /upload/logs`
- `POST /upload/api-traces`
- `POST /upload/db-queries`
- `POST /analyze`
- `GET /issues`

## Frontend dashboard

A React dashboard is available in `frontend/`.

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Start the dashboard locally:

```bash
npm run dev
```

3. Open the URL printed by Vite and ensure the FastAPI backend is running at `http://localhost:8000`.

## Notes

- `OPENAI_API_KEY` is optional; the service falls back to simple heuristics when not provided.
- The vector store uses FAISS for similarity indexing of ingested text.
- PostgreSQL and MongoDB connection settings are configurable via environment variables.
