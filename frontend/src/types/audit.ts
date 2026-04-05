export type AuditEntry = {
  id: string;
  event_type: string;
  details: string;
  created_at?: string;
};

export type ForensicTimelineEvent = {
  event_id: string;
  ts: string;
  event_type: string;
  detection: Record<string, string | number | boolean>;
  context_references: Array<Record<string, string>>;
  audit_linkage: Record<string, string>;
};

export type ForensicTimelineResponse = {
  schema_version: string;
  attack_id: string;
  events: ForensicTimelineEvent[];
  total_events: number;
  data_completeness: string;
};
