import { useMemo, useState } from "react";

import { MainLayout } from "./components/layout/MainLayout";
import type { AppView } from "./components/layout/Sidebar";
import Audit from "./pages/Audit";
import BlindSpots from "./pages/BlindSpots";
import BlueTeam from "./pages/BlueTeam";
import Dashboard from "./pages/Dashboard";
import RedTeam from "./pages/RedTeam";

function pageTitle(view: AppView): string {
  if (view === "redteam") {
    return "Red Team";
  }
  if (view === "blueteam") {
    return "Blue Team";
  }
  if (view === "audit") {
    return "Audit";
  }
  if (view === "blindspots") {
    return "Blind Spots";
  }
  return "Dashboard";
}

function App() {
  const [view, setView] = useState<AppView>("dashboard");

  const content = useMemo(() => {
    if (view === "redteam") {
      return <RedTeam />;
    }
    if (view === "blueteam") {
      return <BlueTeam />;
    }
    if (view === "audit") {
      return <Audit />;
    }
    if (view === "blindspots") {
      return <BlindSpots />;
    }
    return <Dashboard />;
  }, [view]);

  return (
    <MainLayout activeView={view} onSelectView={setView} title={pageTitle(view)}>
      {content}
    </MainLayout>
  );
}

export default App;
