export default function BlindSpots() {
  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 text-slate-100 shadow-panel">
        <p className="text-xs uppercase tracking-[0.2em] text-brand-300">Coverage intelligence</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Blind Spots Workspace</h1>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Blind spot analysis has been streamlined into Blue Team and Audit workflows. This panel remains your strategic summary
          for detection gaps and investigation priorities.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-950/65 p-4 text-sm text-slate-300">
          <h2 className="text-base font-semibold text-slate-100">Current state</h2>
          <p className="mt-2">No unresolved blind spot queue items currently surfaced in this view.</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-950/65 p-4 text-sm text-slate-300">
          <h2 className="text-base font-semibold text-slate-100">Next actions</h2>
          <p className="mt-2">Run new Red Team simulations and review resulting Blue Team narratives to discover coverage gaps.</p>
        </div>
      </div>
    </div>
  );
}
