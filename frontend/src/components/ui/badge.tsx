type BadgeTone = "neutral" | "danger" | "warning" | "safe";

type BadgeProps = {
  label: string;
  tone?: BadgeTone;
};

const toneClassMap: Record<BadgeTone, string> = {
  neutral: "border border-slate-700 bg-slate-800 text-slate-200",
  danger: "border border-red-500/40 bg-red-500/10 text-red-300",
  warning: "border border-amber-400/40 bg-amber-400/10 text-amber-300",
  safe: "border border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
};

export function Badge({ label, tone = "neutral" }: BadgeProps) {
  return <span className={`inline-flex rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] ${toneClassMap[tone]}`}>{label}</span>;
}
