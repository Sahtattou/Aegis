import type { Detection } from "../../types/detection";
import { Card } from "../ui/card";

type DetectionCardProps = {
  detection: Detection | null;
};

export function DetectionCard({ detection }: DetectionCardProps) {
  if (!detection) {
    return (
      <Card>
        <p className="text-sm text-slate-300">No blue-team evaluation yet.</p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="text-lg font-semibold text-slate-100">Blue Team Detection</h2>
      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-400">Decision summary</p>
      <div className="mt-4 grid gap-2 rounded-xl border border-slate-700 bg-slate-950/60 p-4 text-sm text-slate-200 sm:grid-cols-2">
        <p>Decision: {detection.decision}</p>
        <p>Band: {detection.band}</p>
        <p>Threat class: {detection.threat_class}</p>
        <p>Fused confidence: {(detection.fused_confidence * 100).toFixed(1)}%</p>
        <p className="sm:col-span-2">Audit event: {detection.audit_event_id}</p>
      </div>
    </Card>
  );
}
