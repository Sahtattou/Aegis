import type { Attack } from "../../types/attack";
import { Card } from "../ui/card";

type AttackCardProps = {
  attack: Attack | null;
};

export function AttackCard({ attack }: AttackCardProps) {
  return (
    <Card tone="light" className="min-h-[220px]">
      <h2 className="text-lg font-semibold text-slate-900">Latest Attack</h2>
      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-500">Generated simulation output</p>
      {attack ? (
        <article className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex flex-wrap gap-2 text-xs text-slate-500">
            <p>ID: {attack.attack_id}</p>
            <p>Persona: {attack.persona}</p>
            <p>Severity: {attack.severity}</p>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-700">{attack.content}</p>
          <p className="mt-3 text-xs text-slate-500">
            Techniques: {attack.techniques.join(", ")}
          </p>
        </article>
      ) : (
        <p className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
          No simulated attacks yet. Run red team to generate one.
        </p>
      )}
    </Card>
  );
}
