import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost" | "danger";
} & ButtonHTMLAttributes<HTMLButtonElement>;

const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "border border-brand-500/60 bg-brand-500/20 text-brand-100 hover:border-brand-300/70 hover:bg-brand-400/25 focus:ring-brand-300/60",
  secondary:
    "border border-slate-700 bg-slate-800/90 text-slate-100 hover:border-slate-600 hover:bg-slate-700 focus:ring-slate-300/25",
  ghost: "border border-transparent bg-transparent text-slate-300 hover:bg-slate-800 hover:text-white focus:ring-slate-300/20",
  danger:
    "border border-red-500/60 bg-red-500/15 text-red-200 hover:border-red-400/70 hover:bg-red-500/25 focus:ring-red-300/40",
};

export function Button({ children, className, variant = "secondary", ...props }: ButtonProps) {
  const baseClassName =
    "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition duration-200 focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60";

  return (
    <button
      type="button"
      className={`${baseClassName} ${variants[variant]} ${className ?? ""}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}
