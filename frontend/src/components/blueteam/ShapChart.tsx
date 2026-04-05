import type { Detection } from "../../types/detection";
import { Card } from "../ui/card";

type ShapChartProps = {
  detection: Detection | null;
};

export function ShapChart({ detection }: ShapChartProps) {
  const top = detection?.xai_top_contributors ?? [];

  return (
    <Card>
      <h3 className="text-base font-semibold text-slate-100">Top Contributors</h3>
      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-400">Explainability signals</p>
      {top.length === 0 ? (
        <p className="mt-2 text-sm text-slate-300">No contributor data.</p>
      ) : (
        <ul className="mt-3 space-y-2 text-sm">
          {top.map((item, index) => (
            <li key={`${item.feature}-${index}`} className="rounded-xl border border-slate-700 bg-slate-950/70 p-3">
              <p className="font-medium text-slate-100">{String(item.feature)}</p>
              <p className="text-slate-300">Contribution: {Number(item.contribution).toFixed(2)}</p>
              <p className="text-slate-400">Direction: {String(item.direction)}</p>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
