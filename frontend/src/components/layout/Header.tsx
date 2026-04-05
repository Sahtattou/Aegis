type HeaderProps = {
  title: string;
};

export function Header({ title }: HeaderProps) {
  return (
    <header className="border-b border-slate-200 bg-white px-8 py-4">
      <h1 className="text-lg font-semibold text-slate-800">{title}</h1>
      <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-slate-500">
        Security Operations
      </h2>
    </header>
  );
}
