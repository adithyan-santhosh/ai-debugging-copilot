# AI Debugging Copilot

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![FAISS](https://img.shields.io/badge/FAISS-blue?style=for-the-badge&logo=facebook&logoColor=white)
![RAG](https://img.shields.io/badge/Architecture-RAG-orange?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-LLM-white?style=for-the-badge)

A full-stack application for backend system debugging using AI and RAG (Retrieval-Augmented Generation). It ingests logs, API traces, and database queries to detect issues, provide root cause analysis, suggest fixes, and optimize queries.

## 🚀 Features

- **Data Ingestion**: Upload logs, API traces, and DB queries via JSON payloads
- **Intelligent Detection**: Automatically identify slow queries (>500ms), failed API calls (status >=400), and application errors
- **AI-Powered Analysis**: Use OpenAI GPT-4o-mini for summarizing root causes and generating fix suggestions
- **Query Optimization**: Provide SQL optimization hints for slow queries
- **Severity Ranking**: Issues ranked as Critical, High, Medium, Low
- **Interactive Dashboard**: React-based UI for uploading data, viewing issues, and filtering by severity
- **Vector Search**: FAISS-powered similarity search for RAG context
- **Database Support**: Optional async connections to PostgreSQL and MongoDB
- **Real-time Updates**: Issues update immediately after uploads

## 🏗️ Architecture

### High-Level Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   Databases     │
│   (Frontend)    │◄──►│   Backend       │◄──►│   (Optional)    │
│                 │    │                 │    │                 │
│ - Upload Forms  │    │ - REST APIs     │    │ - PostgreSQL    │
│ - Issue Display │    │ - AI Analysis   │    │ - MongoDB       │
│ - Filtering     │    │ - Vector Store  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                          │
                          ▼
                   ┌─────────────────┐
                   │   OpenAI API    │
                   │   (Embeddings   │
                   │    & Chat)      │
                   └─────────────────┘
```

### Component Diagram
```mermaid
graph TB
    A[React Dashboard] --> B[FastAPI Backend]
    B --> C[Data Ingestion Service]
    B --> D[Analysis Service]
    B --> E["Vector Store (FAISS)"]
    B --> F[OpenAI Client]
    D --> F
    C --> E
    B --> G[(PostgreSQL)]
    B --> H[(MongoDB)]
    B --> I[In-Memory Store]

    subgraph "Frontend"
        A
    end

    subgraph "Backend Services"
        C
        D
        E
        F
    end

    subgraph "Data Layer"
        G
        H
        I
    end
```

### Data Flow
1. **User uploads data** via UI → FastAPI validates and stores in memory + indexes in FAISS
2. **User triggers analysis** → Backend detects issues, calls OpenAI for summaries, sorts by time
3. **UI displays issues** → Filtered by severity, with real-time updates

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **AI**: OpenAI API (embeddings + GPT-4o-mini)
- **Vector DB**: FAISS (in-memory similarity search)
- **Databases**: PostgreSQL (asyncpg), MongoDB (motor) - optional
- **Validation**: Pydantic
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Styling**: Custom CSS with dark theme

### Other
- **Environment**: Python 3.10+, Node.js 18+
- **Deployment**: Local development (can be containerized)

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup
1. **Clone and navigate**:
   ```bash
   git clone <repo-url>
   cd ai-debugging-copilot
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env to add OPENAI_API_KEY and optional DB credentials
   ```

5. **Run backend**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup
1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```
   - Opens at `http://localhost:3000`
   - Automatically proxies to backend at `http://localhost:8000`

## 📖 Usage

### API Endpoints
- `GET /health` - Health check
- `POST /upload/logs` - Ingest log entries (array of LogEntry)
- `POST /upload/api-traces` - Ingest API traces (array of APITrace)
- `POST /upload/db-queries` - Ingest DB queries (array of DBQuery)
- `POST /analyze` - Run issue detection and analysis
- `GET /issues` - Retrieve detected issues
- `GET /docs` - Interactive API documentation (Swagger UI)

### Sample Data Upload
Use the UI or curl:

```bash
# Upload DB queries
curl -X POST "http://localhost:8000/upload/db-queries" \
  -H "Content-Type: application/json" \
  -d '[{"query": "SELECT * FROM users WHERE email = '\''user@example.com'\''", "duration_ms": 1100, "database": "postgres", "error": ""}]'
```

### UI Workflow
1. Open `http://localhost:3000`
2. Select tab (Logs, API Traces, DB Queries)
3. Edit JSON payload (samples provided)
4. Click "Upload" (automatically runs analysis)
5. View issues in the list, filtered by severity

## 🔧 Configuration

### Environment Variables (.env)
```env
OPENAI_API_KEY=your_openai_key_here
POSTGRES_DSN=postgresql://user:password@localhost:5432/debugcopilot
MONGO_URI=mongodb://localhost:27017
VECTOR_DIR=./vectors
ENVIRONMENT=development
```

- `OPENAI_API_KEY`: Required for AI analysis (falls back to heuristics if missing)
- `POSTGRES_DSN`: Optional PostgreSQL connection
- `MONGO_URI`: Optional MongoDB connection
- `VECTOR_DIR`: Directory for FAISS index files

## 🐛 Troubleshooting

- **Backend won't start**: Check if port 8000 is free, ensure dependencies installed
- **Upload fails**: Verify JSON format, ensure backend is running
- **No AI summaries**: Add `OPENAI_API_KEY` to .env
- **DB connection errors**: Logged as warnings, app starts without DBs

## 📝 API Reference

### Data Models
- **LogEntry**: `timestamp`, `level`, `message`, `service`, `context`
- **APITrace**: `path`, `method`, `status_code`, `latency_ms`, `request`, `response`, `error`
- **DBQuery**: `query`, `duration_ms`, `database`, `collection`, `error`
- **IssueDetail**: `id`, `category`, `severity`, `title`, `root_cause`, `suggested_fix`, `evidence`, `optimization`, `created_at`

