import { ReactNode } from "react";

type MainLayoutProps = { children?: ReactNode };

export function MainLayout({ children }: MainLayoutProps) {
  return <main>{children}</main>;
}
