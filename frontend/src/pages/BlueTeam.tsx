import { useState } from "react";

import { DetectionCard } from "../components/blueteam/DetectionCard";
import { ShapChart } from "../components/blueteam/ShapChart";
import { XaiNarrative } from "../components/blueteam/XaiNarrative";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { useBlueTeam } from "../hooks/useBlueTeam";
import type { Detection } from "../types/detection";

export default function BlueTeam() {
  const { evaluate, loading, error } = useBlueTeam();
  const [content, setContent] = useState("Please verify password now");
  const [detection, setDetection] = useState<Detection | null>(null);

  async function onEvaluate() {
    try {
      const result = await evaluate({
        attack_id: `frontend-${Date.now()}`,
        content,
        source: "frontend",
        metadata: {},
      });
      setDetection(result);
    } catch {
      setDetection(null);
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <p className="text-xs uppercase tracking-[0.2em] text-brand-300">Detection & response</p>
        <h1 className="mt-2 text-2xl font-semibold text-slate-100">Blue Team Analysis</h1>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Submit suspicious payloads, evaluate detection confidence, and inspect explainability signals.
        </p>
        <textarea
          className="mt-4 h-36 w-full rounded-xl border border-slate-700 bg-slate-950/80 p-4 text-sm text-slate-100 outline-none ring-0 transition focus:border-brand-400"
          value={content}
          onChange={(event) => setContent(event.target.value)}
        />
        <div className="mt-4 flex items-center gap-3">
          <Button variant="primary" onClick={() => void onEvaluate()} disabled={loading}>
            {loading ? "Evaluating..." : "Evaluate"}
          </Button>
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
        </div>
      </Card>

      <DetectionCard detection={detection} />
      <ShapChart detection={detection} />
      <XaiNarrative detection={detection} />
    </div>
  );
}
