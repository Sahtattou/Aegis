import type { Attack } from "../../types/attack";
import { Card } from "../ui/card";

type AttackCardProps = {
  attack: Attack | null;
};

export function AttackCard({ attack }: AttackCardProps) {
  return (
    <Card className="min-h-[180px]">
      <h2 className="text-lg font-semibold text-slate-900">Latest Attack</h2>
      {attack ? (
        <article className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-3">
          <p className="text-xs text-slate-500">ID: {attack.attack_id}</p>
          <p className="text-xs text-slate-500">Persona: {attack.persona}</p>
          <p className="text-xs text-slate-500">Severity: {attack.severity}</p>
          <p className="mt-2 text-sm text-slate-700">{attack.content}</p>
          <p className="mt-2 text-xs text-slate-500">
            Techniques: {attack.techniques.join(", ")}
          </p>
        </article>
      ) : (
        <p className="mt-3 text-sm text-slate-500">No simulated attacks yet. Run red team to generate one.</p>
      )}
    </Card>
  );
}
