import { ReactNode } from "react";

type CardProps = {
  children?: ReactNode;
  className?: string;
};

export function Card({ children, className }: CardProps) {
  const baseClassName = "rounded-xl border border-slate-800 bg-slate-900 p-4 text-slate-100 shadow-lg shadow-slate-950/40";
  return <div className={`${baseClassName} ${className ?? ""}`.trim()}>{children}</div>;
}
