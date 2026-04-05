import { ReactNode } from "react";

import { Header } from "./Header";
import { AppView, Sidebar } from "./Sidebar";

type MainLayoutProps = {
  children?: ReactNode;
  activeView: AppView;
  onSelectView: (view: AppView) => void;
  title: string;
};

export function MainLayout({ children, activeView, onSelectView, title }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Header title={title} />
      <div className="flex min-h-[calc(100vh-110px)]">
        <Sidebar activeView={activeView} onSelectView={onSelectView} />
        <main className="aegis-grid flex-1 bg-slate-900/50 p-8 lg:p-10">{children}</main>
      </div>
    </div>
  );
}
