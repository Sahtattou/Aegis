import type { Detection } from "../../types/detection";
import { Card } from "../ui/card";

type XaiNarrativeProps = {
  detection: Detection | null;
};

export function XaiNarrative({ detection }: XaiNarrativeProps) {
  return (
    <Card>
      <h3 className="text-base font-semibold text-slate-100">XAI Narrative</h3>
      <p className="mt-2 text-sm text-slate-300">
        {detection?.explanation_fr ?? "No explainability narrative available."}
      </p>
    </Card>
  );
}
