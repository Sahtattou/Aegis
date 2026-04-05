type HeaderProps = {
  title: string;
};

export function Header({ title }: HeaderProps) {
  return (
    <header className="aegis-grid border-b border-slate-800 bg-slate-950 px-8 py-5">
      <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-brand-300/90">HARIS Platform</p>
      <h1 className="mt-1 text-2xl font-semibold text-white">{title}</h1>
      <h2 className="text-xs font-medium uppercase tracking-[0.16em] text-slate-400">
        Security Operations
      </h2>
    </header>
  );
}
