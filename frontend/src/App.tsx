import { useMemo, useState } from "react";

import { AttackTimeline } from "./components/dashboard/AttackTimeline";
import { MainLayout } from "./components/layout/MainLayout";
import { AttackCard } from "./components/redteam/AttackCard";
import { RunRedTeamButton } from "./components/redteam/RunRedTeamButton";
import { Card } from "./components/ui/card";
import { attackStore } from "./stores/attackStore";
import type { Attack } from "./types/attack";

function App() {
  const [attacks, setAttacks] = useState<Attack[]>(attackStore.attacks);

  const latestAttack = useMemo(() => {
    if (attacks.length === 0) {
      return null;
    }
    return attacks[attacks.length - 1];
  }, [attacks]);

  const handleRunRedTeam = () => {
    const attack: Attack = {
      id: `sim-${Date.now()}`,
      content: "Simulated social-engineering chain started against dashboard target (placeholder).",
    };
    attackStore.attacks = [...attackStore.attacks, attack];
    setAttacks(attackStore.attacks);
  };

  return (
    <MainLayout>
      <section className="space-y-4 rounded-lg border border-dashed border-slate-300 bg-white p-6">
        <header>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="mt-2 text-sm text-slate-600">
            Red Team controls are scaffolded and ready to connect to backend orchestration.
          </p>
        </header>

        <Card className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Run Red Team</h2>
            <p className="text-sm text-slate-600">Launch a simulated attack chain and inspect generated entries.</p>
          </div>
          <RunRedTeamButton onRun={handleRunRedTeam} />
        </Card>

        <div className="grid gap-4 lg:grid-cols-2">
          <AttackCard attack={latestAttack} />
          <AttackTimeline attacks={attacks} />
        </div>
      </section>
    </MainLayout>
  );
}

export default App;
