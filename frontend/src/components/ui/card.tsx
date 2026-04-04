import { ReactNode } from "react";

type CardProps = { children?: ReactNode };

export function Card({ children }: CardProps) {
  return <div>{children}</div>;
}
