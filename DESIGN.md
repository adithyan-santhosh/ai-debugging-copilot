# AI Debugging Copilot: Complete Low-Level Design and Flow

## 1. Project Overview

The AI Debugging Copilot is a full-stack application that ingests logs, API traces, and database queries, uses AI (OpenAI) and Retrieval-Augmented Generation (RAG) to analyze issues, and provides root cause analysis, fixes, and optimizations via a React dashboard.

**Key Features:**
- Ingest data from logs, API traces, DB queries
- Detect slow queries, failed APIs, errors
- AI-powered explanations using OpenAI GPT
- Vector search with FAISS for RAG
- Severity-ranked issue dashboard
- Async DB connections (PostgreSQL, MongoDB)

**Tech Stack:**
- Backend: FastAPI (Python), OpenAI API, FAISS, asyncpg, motor
- Frontend: React (TypeScript), Vite, Axios
- DB: PostgreSQL (optional), MongoDB (optional)

## 2. Architecture

### High-Level Architecture
- **Frontend**: React app for UI, sends HTTP requests to backend
- **Backend**: FastAPI server handling ingestion, analysis, AI calls
- **Data Layer**: In-memory storage + optional DBs + FAISS vector store
- **AI Layer**: OpenAI for embeddings and summarization

### Directory Structure
```
ai-debugging-copilot/
├── app/                          # Backend package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, routes, startup
│   ├── config.py                 # Settings (env vars)
│   ├── schemas.py                # Pydantic models (LogEntry, APITrace, etc.)
│   ├── db.py                     # DB connection helpers
│   ├── core/
│   │   ├── __init__.py
│   │   └── openai_client.py      # OpenAI API calls
│   └── services/
│       ├── __init__.py
│       ├── ingestion.py          # Data ingestion logic
│       ├── analysis.py           # Issue detection and AI summarization
│       └── vectorstore.py        # FAISS indexing
├── frontend/                     # React app
│   ├── src/
│   │   ├── App.tsx               # Main UI component
│   │   ├── main.tsx              # React entry point
│   │   ├── types.ts              # TypeScript interfaces
│   │   ├── styles.css            # CSS
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
├── requirements.txt              # Python deps
├── .env.example                  # Env template
├── README.md                     # Docs
└── .gitignore
```

## 3. Components

### Backend Components

#### `app/main.py`
- **FastAPI App**: Initializes app with CORS, routes
- **Routes**:
  - `GET /health`: Health check
  - `POST /upload/logs`: Ingest logs (expects list[LogEntry])
  - `POST /upload/api-traces`: Ingest API traces (list[APITrace])
  - `POST /upload/db-queries`: Ingest DB queries (list[DBQuery])
  - `POST /analyze`: Run analysis (returns list[IssueDetail])
  - `GET /issues`: Get cached issues
- **Startup/Shutdown**: Connect/disconnect DBs (with error handling)

#### `app/schemas.py`
- **Models**:
  - `LogEntry`: timestamp, level, message, service, context
  - `APITrace`: path, method, status_code, latency_ms, request, response, error
  - `DBQuery`: query, duration_ms, database, collection, error
  - `IssueDetail`: id, category, severity, title, root_cause, suggested_fix, evidence, optimization
  - `IngestResponse`: accepted (int), message
  - `AnalyzeRequest`: include_logs, include_api_traces, include_db_queries

#### `app/services/ingestion.py`
- **IngestionStore**: In-memory lists for logs, api_traces, db_queries, issues
- **Functions**:
  - `ingest_logs()`: Append to store, index texts
  - `ingest_api_traces()`: Append, index
  - `ingest_db_queries()`: Append, index

#### `app/services/analysis.py`
- **Detection Functions**:
  - `_detect_slow_queries()`: Check db_queries for duration_ms > 500, create IssueDetail
  - `_detect_failed_api_calls()`: Check api_traces for status_code >= 400
  - `_detect_errors()`: Regex match "exception|error|failed" in logs
- **analyze_issues()**: Run detections, sort by severity, call AI for api/db issues

#### `app/services/vectorstore.py`
- **FAISS Index**: Load/save to VECTOR_DIR/faiss.index
- **index_entries()**: Embed texts via OpenAI, add to index, save text store

#### `app/core/openai_client.py`
- **embed_texts()**: Call OpenAI Embedding API (text-embedding-3-small)
- **summarize_issue()**: Call GPT-4o-mini for root cause summary

#### `app/config.py`
- **Settings Class**: Load from env (OPENAI_API_KEY, POSTGRES_DSN, etc.)

#### `app/db.py`
- **connect_postgres()**: asyncpg pool
- **connect_mongo()**: motor client

### Frontend Components

#### `frontend/src/App.tsx`
- **State**: issues, activeTab, payload, message, loading
- **Functions**:
  - `fetchIssues()`: GET /issues
  - `uploadPayload()`: JSON.parse, POST to endpoint
  - `analyze()`: POST /analyze, then fetchIssues
- **UI**: Tabs for upload, summary grid, issue list

#### `frontend/src/types.ts`
- TypeScript interfaces matching backend schemas

## 4. Data Flow

1. **User Uploads Data**:
   - Frontend: User selects tab, edits JSON, clicks upload
   - Axios POST to backend endpoint (e.g., /upload/db-queries)
   - Backend: Validate via Pydantic, append to IngestionStore, index in FAISS

2. **User Runs Analysis**:
   - Frontend: POST /analyze
   - Backend: Run detection functions, generate issues, call OpenAI if key set, return issues
   - Frontend: Display issues

3. **AI Processing**:
   - For each issue (api/db): Embed evidence, summarize with GPT

## 5. Step-by-Step Flow

### Setup
1. Clone repo
2. Backend: `python -m venv .venv`, `pip install -r requirements.txt`
3. Frontend: `cd frontend`, `npm install`
4. Copy `.env.example` to `.env`, set OPENAI_API_KEY

### Run
1. Backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Frontend: `npm run dev` (runs on 3000)

### Usage
1. Open `http://localhost:3000/`
2. Select "DB Queries" tab
3. Edit JSON (e.g., add query with duration_ms > 500)
4. Click "Upload DB queries"
5. Click "Run analysis"
6. View issues in list, ranked by severity

### Internal Flow (Upload DB Query)
1. User clicks upload
2. `uploadPayload()`: JSON.parse(payload)
3. Axios POST to `http://localhost:8000/upload/db-queries` with parsed array
4. Backend: Validate as list[DBQuery]
5. `ingest_db_queries()`: Append to store, call `index_entries(["QUERY: {query}"])`
6. `index_entries()`: Embed via OpenAI, add to FAISS index
7. Return IngestResponse

### Internal Flow (Analyze)
1. User clicks analyze
2. Axios POST to `/analyze` with {include_logs: true, ...}
3. Backend: `analyze_issues()`
4. Run `_detect_slow_queries()`, etc.
5. For each issue: If category in ["api", "db"], call `summarize_issue(root_cause, evidence)`
6. `summarize_issue()`: Prompt GPT with root_cause + evidence, return summary
7. Sort issues by severity.value (critical > high > medium > low)
8. Return list[IssueDetail]

## 6. Technologies in Detail

- **FastAPI**: Async web framework, auto-docs at /docs
- **Pydantic**: Data validation
- **FAISS**: Vector similarity search for RAG
- **OpenAI**: Embeddings (1536-dim) and chat completions
- **asyncpg/motor**: Async DB drivers
- **React/Vite**: Modern frontend with hot reload
- **Axios**: HTTP client

## 7. Error Handling

- Backend: DB connection failures logged as warnings, app starts anyway
- Frontend: Catches JSON parse errors, network errors, shows detailed messages
- AI: Falls back to basic text if OPENAI_API_KEY not set

## 8. Security/Performance

- No auth implemented (add for production)
- In-memory storage (use DB for persistence)
- Vector store saved to disk
- CORS enabled for frontend

This covers the complete flow. Let me know if you need code snippets or expansions!