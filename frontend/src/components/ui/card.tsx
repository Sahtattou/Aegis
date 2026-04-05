import { ReactNode } from "react";

type CardProps = {
  children?: ReactNode;
  className?: string;
  tone?: "dark" | "light";
};

const toneMap: Record<NonNullable<CardProps["tone"]>, string> = {
  dark: "rounded-2xl border border-slate-800/80 bg-slate-900/80 p-5 text-slate-100 shadow-panel backdrop-blur",
  light: "rounded-2xl border border-slate-200/80 bg-white p-5 text-slate-900 shadow-lg shadow-slate-900/5",
};

export function Card({ children, className, tone = "dark" }: CardProps) {
  const baseClassName = toneMap[tone];
  return <div className={`${baseClassName} ${className ?? ""}`.trim()}>{children}</div>;
}
