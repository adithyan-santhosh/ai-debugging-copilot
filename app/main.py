import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from .config import get_settings
from .schemas import LogEntry, APITrace, DBQuery, IngestResponse, IssueDetail, AnalyzeRequest
from .services.ingestion import ingestion_store, ingest_logs, ingest_api_traces, ingest_db_queries
from .services.analysis import analyze_issues
from .db import connect_postgres, connect_mongo, close_db_connections

settings = get_settings()
log = logging.getLogger("app.main")
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        await connect_postgres()
    except Exception as exc:
        log.warning("PostgreSQL not available on startup: %s", exc)

    try:
        await connect_mongo()
    except Exception as exc:
        log.warning("MongoDB not available on startup: %s", exc)


@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connections()


@app.get("/health")
async def health_check():
    return {"status": "ok", "application": settings.app_name}


@app.post("/upload/logs", response_model=IngestResponse)
async def upload_logs(entries: list[LogEntry]):
    count = await ingest_logs(entries)
    return IngestResponse(accepted=count, message=f"{count} log entries ingested")


@app.post("/upload/api-traces", response_model=IngestResponse)
async def upload_api_traces(entries: list[APITrace]):
    count = await ingest_api_traces(entries)
    return IngestResponse(accepted=count, message=f"{count} api traces ingested")


@app.post("/upload/db-queries", response_model=IngestResponse)
async def upload_db_queries(entries: list[DBQuery]):
    count = await ingest_db_queries(entries)
    return IngestResponse(accepted=count, message=f"{count} db queries ingested")


@app.post("/analyze", response_model=list[IssueDetail])
async def analyze(payload: AnalyzeRequest):
    issues = await analyze_issues(
        include_logs=payload.include_logs,
        include_api_traces=payload.include_api_traces,
        include_db_queries=payload.include_db_queries,
    )
    if not issues:
        raise HTTPException(status_code=404, detail="No actionable issues were found.")
    return issues


@app.get("/issues", response_model=list[IssueDetail])
async def list_issues():
    if not ingestion_store.issues:
        issues = await analyze_issues(True, True, True)
        ingestion_store.issues = issues
    return ingestion_store.issues
