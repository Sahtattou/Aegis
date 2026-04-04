import type { Attack } from "../../types/attack";
import { Card } from "../ui/card";

type AttackTimelineProps = {
  attacks: Attack[];
};

export function AttackTimeline({ attacks }: AttackTimelineProps) {
  return (
    <Card className="min-h-[180px]">
      <h2 className="text-lg font-semibold text-slate-900">Attack Timeline</h2>
      {attacks.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">Timeline is empty until a simulation runs.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {attacks.slice(0, 5).map((attack) => (
            <li key={attack.id} className="rounded-md border border-slate-200 bg-slate-50 p-2 text-sm text-slate-700">
              {attack.content}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
