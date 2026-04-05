type BadgeTone = "neutral" | "danger" | "warning" | "safe";

type BadgeProps = {
  label: string;
  tone?: BadgeTone;
};

const toneClassMap: Record<BadgeTone, string> = {
  neutral: "border border-slate-600/70 bg-slate-700/30 text-slate-200",
  danger: "border border-red-400/40 bg-red-500/15 text-red-200",
  warning: "border border-amber-300/40 bg-amber-400/15 text-amber-100",
  safe: "border border-emerald-400/40 bg-emerald-500/15 text-emerald-100",
};

export function Badge({ label, tone = "neutral" }: BadgeProps) {
  return <span className={`inline-flex rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] ${toneClassMap[tone]}`}>{label}</span>;
}
