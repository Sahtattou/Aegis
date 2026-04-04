import { ReactNode } from "react";

type CardProps = {
  children?: ReactNode;
  className?: string;
};

export function Card({ children, className }: CardProps) {
  const baseClassName = "rounded-lg border border-slate-200 bg-white p-4";
  return <div className={`${baseClassName} ${className ?? ""}`.trim()}>{children}</div>;
}
