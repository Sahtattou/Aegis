import type { Attack } from "../../types/attack";
import { Card } from "../ui/card";

type AttackTimelineProps = {
  attacks: Attack[];
};

export function AttackTimeline({ attacks }: AttackTimelineProps) {
  return (
    <Card tone="light" className="min-h-[220px]">
      <h2 className="text-lg font-semibold text-slate-900">Attack Timeline</h2>
      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-500">Recent simulations</p>
      {attacks.length === 0 ? (
        <p className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
          Timeline is empty until a simulation runs.
        </p>
      ) : (
        <ul className="mt-4 space-y-2">
          {attacks.slice(0, 5).map((attack) => (
            <li
              key={attack.attack_id}
              className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700"
            >
              <p className="font-medium text-slate-900">{attack.attack_id}</p>
              <p>{attack.content}</p>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
