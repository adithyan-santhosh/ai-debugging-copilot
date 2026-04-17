import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { IssueDetail, IssueSeverity, UploadType } from './types'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const severityClasses: Record<IssueSeverity, string> = {
  critical: 'badge critical',
  high: 'badge high',
  medium: 'badge medium',
  low: 'badge low',
}

const uploadEndpoints: Record<UploadType, string> = {
  logs: '/upload/logs',
  apiTraces: '/upload/api-traces',
  dbQueries: '/upload/db-queries',
}

const defaultJson = {
  logs: '[{ "timestamp": "2026-04-17T12:00:00Z", "level": "ERROR", "message": "Database timeout error", "service": "auth-service" }]',
  apiTraces: '[{ "path": "/api/login", "method": "POST", "status_code": 500, "latency_ms": 680, "request": {"email": "user@example.com"}, "response": {"error": "Internal server error"}, "error": "500 Internal Server Error" }]',
  dbQueries: '[{ "query": "SELECT * FROM users WHERE email = \"user@example.com\"", "duration_ms": 1100, "database": "postgres", "error": "" }]',
}

function App() {
  const [issues, setIssues] = useState<IssueDetail[]>([])
  const [activeTab, setActiveTab] = useState<UploadType>('logs')
  const [payload, setPayload] = useState(defaultJson.logs)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const selectedEndpoint = uploadEndpoints[activeTab]

  useEffect(() => {
    const value = defaultJson[activeTab]
    setPayload(value)
  }, [activeTab])

  const issueCounts = useMemo(() => {
    return issues.reduce<Record<IssueSeverity, number>>(
      (acc, issue) => {
        acc[issue.severity] = (acc[issue.severity] || 0) + 1
        return acc
      },
      { critical: 0, high: 0, medium: 0, low: 0 },
    )
  }, [issues])

  const fetchIssues = async () => {
    setLoading(true)
    setMessage('Loading issues...')
    try {
      const response = await axios.get<IssueDetail[]>(`${apiBaseUrl}/issues`)
      setIssues(response.data)
      setMessage(`Loaded ${response.data.length} issue(s)`)
    } catch (error) {
      setMessage('No issues found yet. Upload data and analyze.')
      setIssues([])
    } finally {
      setLoading(false)
    }
  }

  const uploadPayload = async () => {
    setLoading(true)
    setMessage('Uploading payload...')
    try {
      const parsed = JSON.parse(payload)
      await axios.post(`${apiBaseUrl}${selectedEndpoint}`, parsed)
      setMessage('Upload successful. Run analysis to refresh issues.')
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
      setMessage(`Upload failed: ${errorMsg}. Ensure the JSON payload is valid and the backend is running.`)
    } finally {
      setLoading(false)
    }
  }

  const analyze = async () => {
    setLoading(true)
    setMessage('Analyzing data...')
    try {
      await axios.post(`${apiBaseUrl}/analyze`, {
        include_logs: true,
        include_api_traces: true,
        include_db_queries: true,
      })
      await fetchIssues()
      setMessage('Analysis complete.')
    } catch (error) {
      setMessage('Analysis failed. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-shell">
      <header>
        <div>
          <h1>AI Debugging Copilot</h1>
          <p>Upload logs, API traces, and DB queries, then inspect issues ranked by severity.</p>
        </div>
        <div className="actions">
          <button onClick={fetchIssues} disabled={loading}>Refresh issues</button>
          <button onClick={analyze} disabled={loading}>Run analysis</button>
        </div>
      </header>

      <section className="grid-2">
        <div className="panel">
          <h2>Upload data</h2>
          <div className="tabs">
            <button className={activeTab === 'logs' ? 'active' : ''} onClick={() => setActiveTab('logs')}>Logs</button>
            <button className={activeTab === 'apiTraces' ? 'active' : ''} onClick={() => setActiveTab('apiTraces')}>API Traces</button>
            <button className={activeTab === 'dbQueries' ? 'active' : ''} onClick={() => setActiveTab('dbQueries')}>DB Queries</button>
          </div>
          <textarea value={payload} onChange={(event) => setPayload(event.target.value)} rows={14} />
          <button onClick={uploadPayload} disabled={loading}>Upload {activeTab === 'apiTraces' ? 'API traces' : activeTab === 'dbQueries' ? 'DB queries' : 'logs'}</button>
          <p className="hint">Posting to <code>{selectedEndpoint}</code></p>
        </div>

        <div className="panel status-panel">
          <h2>Issue summary</h2>
          <div className="summary-grid">
            {(['critical', 'high', 'medium', 'low'] as IssueSeverity[]).map((level) => (
              <div key={level} className="summary-card">
                <strong>{level}</strong>
                <span>{issueCounts[level]}</span>
              </div>
            ))}
          </div>
          <div className="message-box">{message}</div>
          <div className="panel-footer">
            <strong>API Base URL:</strong> {apiBaseUrl}
          </div>
        </div>
      </section>

      <section className="panel issue-list">
        <h2>Detected issues</h2>
        {issues.length === 0 ? (
          <p>No issues available. Upload example data and press "Run analysis".</p>
        ) : (
          issues.map((issue) => (
            <article key={issue.id} className="issue-card">
              <div className="issue-header">
                <h3>{issue.title}</h3>
                <span className={severityClasses[issue.severity]}>{issue.severity.toUpperCase()}</span>
              </div>
              <p><strong>Category:</strong> {issue.category}</p>
              <p><strong>Root cause:</strong> {issue.root_cause}</p>
              <p><strong>Suggested fix:</strong> {issue.suggested_fix}</p>
              {issue.optimization ? <p><strong>Optimization:</strong> {issue.optimization}</p> : null}
              <div className="evidence">
                <strong>Evidence</strong>
                <ul>{issue.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul>
              </div>
            </article>
          ))
        )}
      </section>
    </div>
  )
}

export default App
