import { useSSE } from "../hooks/useSSE";
import { Card } from "../components/ui/card";

export default function Dashboard() {
  const { status, error, lastEvent } = useSSE(true);

  return (
    <div className="space-y-6">
      <Card>
        <p className="text-xs uppercase tracking-[0.2em] text-brand-300">SOC overview</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Dashboard Command Center</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
          Monitor event pipeline health, track the most recent intelligence, and quickly pivot into Red or Blue Team workflows.
        </p>
      </Card>

      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-white">Event Stream</h2>
          <p className="mt-1 text-sm text-slate-400">Current stream health and most recent payload.</p>
          <div className="mt-4 rounded-xl border border-slate-700 bg-slate-950/60 p-4">
            <p className="text-sm text-slate-200">Status: <span className="font-semibold text-brand-200">{status}</span></p>
            {lastEvent ? <p className="mt-2 text-sm text-slate-300">Last event: {lastEvent}</p> : null}
            {error ? <p className="mt-2 text-sm text-red-300">{error}</p> : null}
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-white">Operational Notes</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li className="rounded-lg border border-slate-700 bg-slate-950/55 p-3">Use Red Team to generate fresh simulated attacks.</li>
            <li className="rounded-lg border border-slate-700 bg-slate-950/55 p-3">Use Blue Team to evaluate incoming malicious content.</li>
            <li className="rounded-lg border border-slate-700 bg-slate-950/55 p-3">Review Audit for traceability and timeline analysis.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
