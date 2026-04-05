import { useState } from "react";

import { AttackCard } from "../components/redteam/AttackCard";
import { RunRedTeamButton } from "../components/redteam/RunRedTeamButton";
import { Card } from "../components/ui/card";
import { useRedTeam } from "../hooks/useRedTeam";
import type { Attack } from "../types/attack";

export default function RedTeam() {
  const { run, loading, error } = useRedTeam();
  const [latestAttack, setLatestAttack] = useState<Attack | null>(null);

  async function onRun() {
    try {
      const result = await run({
        target: "mail-gateway",
        objective: "phishing-resilience",
        n_attacks: 1,
      });
      setLatestAttack(result.attacks[0] ?? null);
    } catch {
      setLatestAttack(null);
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <h1 className="text-xl font-semibold text-slate-100">Red Team</h1>
        <div className="mt-3 flex items-center gap-3">
          <RunRedTeamButton onRun={() => void onRun()} />
          {loading ? <p className="text-sm text-slate-300">Running...</p> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
        </div>
      </Card>
      <AttackCard attack={latestAttack} />
    </div>
  );
}
