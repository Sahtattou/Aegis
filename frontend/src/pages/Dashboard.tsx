import { useSSE } from "../hooks/useSSE";
import { Card } from "../components/ui/card";

export default function Dashboard() {
  const { status, error, lastEvent } = useSSE(true);

  return (
    <Card>
      <h1 className="text-xl font-semibold text-slate-100">Dashboard</h1>
      <p className="mt-3 text-sm text-slate-300">Event stream status: {status}</p>
      {lastEvent ? <p className="text-sm text-slate-300">Last event: {lastEvent}</p> : null}
      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </Card>
  );
}
