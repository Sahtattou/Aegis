import { useAudit } from "../../hooks/useAudit";
import { Card } from "../ui/card";

export function AuditTimeline() {
  const { timeline, loading, error } = useAudit();

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-100">Audit Timeline</h2>
      {loading ? <p className="mt-3 text-sm text-slate-400">Loading...</p> : null}
      {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
      {!loading && !error && timeline.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400">No audit events yet.</p>
      ) : null}
      <ul className="mt-3 space-y-2">
        {timeline.map((event) => (
          <li key={event.id} className="rounded border border-slate-700 bg-slate-950/60 p-3 text-sm">
            <p className="font-medium text-slate-100">{event.event_type}</p>
            <p className="text-slate-300">{event.details}</p>
          </li>
        ))}
      </ul>
    </Card>
  );
}
