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
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <Header title={title} />
      <div className="flex min-h-[calc(100vh-57px)]">
        <Sidebar activeView={activeView} onSelectView={onSelectView} />
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
