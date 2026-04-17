export type UploadType = 'logs' | 'apiTraces' | 'dbQueries'

export type IssueSeverity = 'critical' | 'high' | 'medium' | 'low'

export interface IssueDetail {
  id: string
  category: string
  severity: IssueSeverity
  title: string
  root_cause: string
  suggested_fix: string
  evidence: string[]
  optimization?: string
}
