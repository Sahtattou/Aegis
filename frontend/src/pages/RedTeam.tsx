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
    <div className="space-y-6">
      <Card>
        <p className="text-xs uppercase tracking-[0.2em] text-brand-300">Adversarial simulation</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Red Team Operations</h1>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Launch controlled attack simulations to generate realistic payloads and feed downstream Blue Team detection.
        </p>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <RunRedTeamButton onRun={() => void onRun()} />
          {loading ? <p className="text-sm text-brand-200">Running simulation...</p> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
        </div>
      </Card>
      <AttackCard attack={latestAttack} />
    </div>
  );
}
