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
    <aside className="w-64 border-r border-slate-200 bg-slate-900 px-4 py-6 text-slate-100">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Aegis</p>
        <h1 className="mt-2 text-lg font-semibold">Dashboard</h1>
      </div>

      <nav aria-label="Sidebar navigation">
        <ul className="space-y-2">
          {navigationItems.map((item) => (
            <li key={item.key}>
              <button
                type="button"
                className={
                  item.key === activeView
                    ? "w-full rounded-md bg-slate-800 px-3 py-2 text-left text-sm text-white"
                    : "w-full rounded-md px-3 py-2 text-left text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
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
