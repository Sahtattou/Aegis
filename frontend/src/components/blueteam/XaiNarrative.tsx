import type { Detection } from "../../types/detection";
import { Card } from "../ui/card";

type XaiNarrativeProps = {
  detection: Detection | null;
};

export function XaiNarrative({ detection }: XaiNarrativeProps) {
  return (
    <Card>
      <h3 className="text-base font-semibold text-slate-100">XAI Narrative</h3>
      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-400">Analyst explanation</p>
      <p className="mt-3 rounded-xl border border-slate-700 bg-slate-950/60 p-4 text-sm leading-6 text-slate-300">
        {detection?.explanation_fr ?? "No explainability narrative available."}
      </p>
    </Card>
  );
}
