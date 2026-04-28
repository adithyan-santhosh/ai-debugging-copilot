from ..schemas import LogEntry, APITrace, DBQuery, IssueDetail, IssueSeverity
from .vectorstore import index_entries


class IngestionStore:
    def __init__(self):
        self.logs: list[LogEntry] = []
        self.api_traces: list[APITrace] = []
        self.db_queries: list[DBQuery] = []
        self.issues: list[IssueDetail] = []


ingestion_store = IngestionStore()


async def ingest_logs(entries: list[LogEntry]) -> int:
    ingestion_store.logs.extend(entries)
    await index_entries([f"LOG: {entry.level}: {entry.message}" for entry in entries])
    return len(entries)


async def ingest_api_traces(entries: list[APITrace]) -> int:
    ingestion_store.api_traces.extend(entries)
    await index_entries([f"API {entry.method} {entry.path} {entry.status_code}" for entry in entries])
    return len(entries)


async def ingest_db_queries(entries: list[DBQuery]) -> int:
    ingestion_store.db_queries.extend(entries)
    await index_entries([f"QUERY: {entry.query}" for entry in entries])
    return len(entries)
