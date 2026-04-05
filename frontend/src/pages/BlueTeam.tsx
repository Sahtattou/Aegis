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
    <div className="space-y-4">
      <Card>
        <h1 className="text-xl font-semibold text-slate-100">Blue Team</h1>
        <textarea
          className="mt-3 h-32 w-full rounded border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100"
          value={content}
          onChange={(event) => setContent(event.target.value)}
        />
        <div className="mt-3 flex items-center gap-3">
          <Button onClick={() => void onEvaluate()} disabled={loading}>
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
