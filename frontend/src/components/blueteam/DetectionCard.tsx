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
      <div className="mt-3 space-y-1 text-sm text-slate-300">
        <p>Decision: {detection.decision}</p>
        <p>Band: {detection.band}</p>
        <p>Threat class: {detection.threat_class}</p>
        <p>Fused confidence: {(detection.fused_confidence * 100).toFixed(1)}%</p>
        <p>Audit event: {detection.audit_event_id}</p>
      </div>
    </Card>
  );
}
