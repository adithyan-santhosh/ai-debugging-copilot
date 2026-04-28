import re
import uuid
from typing import List
from ..schemas import IssueDetail, IssueSeverity
from .ingestion import ingestion_store
from ..core.openai_client import summarize_issue


def _detect_slow_queries() -> List[IssueDetail]:
    issues = []
    for query in ingestion_store.db_queries:
        severity = IssueSeverity.low
        if query.duration_ms:
            if query.duration_ms > 1000:
                severity = IssueSeverity.critical
            elif query.duration_ms > 500:
                severity = IssueSeverity.high
            else:
                severity = IssueSeverity.medium
        title = "Database query executed"
        issues.append(
            IssueDetail(
                id=str(uuid.uuid4()),
                category="db",
                severity=severity,
                title=title,
                root_cause=f"Query executed: {query.query}" + (f" in {query.duration_ms}ms" if query.duration_ms else ""),
                suggested_fix="Review query performance and optimize if slow.",
                evidence=[query.query],
                optimization=_suggest_sql_optimization(query.query) if severity in [IssueSeverity.high, IssueSeverity.critical] else None,
            )
        )
    return issues


def _detect_failed_api_calls() -> List[IssueDetail]:
    issues = []
    for trace in ingestion_store.api_traces:
        if trace.status_code >= 400:
            severity = IssueSeverity.critical if trace.status_code >= 500 else IssueSeverity.medium
            title = f"API failure: {trace.method} {trace.path} returned {trace.status_code}"
            issues.append(
                IssueDetail(
                    id=str(uuid.uuid4()),
                    category="api",
                    severity=severity,
                    title=title,
                    root_cause=trace.error or f"Status code {trace.status_code} returned from API",
                    suggested_fix="Inspect the upstream service, validate request payloads, and add error handling for failed responses.",
                    evidence=[f"{trace.method} {trace.path} -> {trace.status_code}"],
                )
            )
    return issues


def _detect_errors() -> List[IssueDetail]:
    issues = []
    for log in ingestion_store.logs:
        if re.search(r"exception|traceback|error|failed", log.message, re.IGNORECASE):
            issues.append(
                IssueDetail(
                    id=str(uuid.uuid4()),
                    category="log",
                    severity=IssueSeverity.high,
                    title="Application error detected in logs",
                    root_cause=log.message,
                    suggested_fix="Investigate the stack trace and correlate with the API and database activity around this timestamp.",
                    evidence=[log.timestamp, log.level, log.message],
                )
            )
    return issues


def _suggest_sql_optimization(query: str) -> str:
    if "select" in query.lower() and "where" in query.lower():
        return "Consider adding an index on the filtered columns used in WHERE clauses and avoid full table scans."
    return "Evaluate if this query can be rewritten with explicit joins or filtered earlier in the pipeline."


async def analyze_issues(include_logs: bool = True, include_api_traces: bool = True, include_db_queries: bool = True) -> List[IssueDetail]:
    findings: List[IssueDetail] = []
    if include_db_queries:
        findings.extend(_detect_slow_queries())
    if include_api_traces:
        findings.extend(_detect_failed_api_calls())
    if include_logs:
        findings.extend(_detect_errors())

    for issue in findings:
        if issue.category in {"api", "db"}:
            issue.root_cause = await summarize_issue(issue.root_cause, issue.evidence)
    findings.sort(key=lambda item: item.severity.value)
    ingestion_store.issues = findings
    return findings
