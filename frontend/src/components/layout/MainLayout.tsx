import { ReactNode } from "react";

import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

type MainLayoutProps = { children?: ReactNode };

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <Header />
      <div className="flex min-h-[calc(100vh-57px)]">
        <Sidebar />
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
