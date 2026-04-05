export type AppView = "dashboard" | "redteam" | "blueteam" | "audit" | "blindspots";

type SidebarProps = {
  activeView: AppView;
  onSelectView: (view: AppView) => void;
};

const navigationItems: Array<{ key: AppView; label: string }> = [
  { key: "dashboard", label: "Dashboard" },
  { key: "redteam", label: "Red Team" },
  { key: "blueteam", label: "Blue Team" },
  { key: "audit", label: "Audit" },
  { key: "blindspots", label: "Blind Spots" },
];

export function Sidebar({ activeView, onSelectView }: SidebarProps) {
  return (
    <aside className="w-72 border-r border-slate-800 bg-slate-950 px-5 py-6 text-slate-100">
      <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
        <p className="text-xs uppercase tracking-[0.24em] text-brand-300">Aegis</p>
        <h1 className="mt-2 text-lg font-semibold text-white">Security Console</h1>
        <p className="mt-1 text-xs text-slate-400">Threat simulation & detection</p>
      </div>

      <nav aria-label="Sidebar navigation">
        <ul className="space-y-2.5">
          {navigationItems.map((item) => (
            <li key={item.key}>
              <button
                type="button"
                className={
                  item.key === activeView
                    ? "w-full rounded-xl border border-brand-500/40 bg-brand-500/20 px-4 py-3 text-left text-sm font-semibold text-brand-100"
                    : "w-full rounded-xl border border-transparent px-4 py-3 text-left text-sm font-medium text-slate-300 transition hover:border-slate-700 hover:bg-slate-900 hover:text-white"
                }
                onClick={() => onSelectView(item.key)}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
