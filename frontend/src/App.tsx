import { useState, useEffect, useCallback } from "react";
import type { ProductReadinessRead } from "./api/types";
import { getProductReadiness } from "./api/product";
import { SetupReadinessView } from "./components/SetupReadinessView";
import { CapabilitiesView } from "./components/CapabilitiesView";
import { StartupListView } from "./components/StartupListView";
import { StartupDetailPanel } from "./components/StartupDetailPanel";
import { AnalysisRunDetailView } from "./components/AnalysisRunDetailView";
import { OpportunitiesView } from "./components/OpportunitiesView";
import { DossierView } from "./components/DossierView";

type ActiveView =
  | "setup"
  | "capabilities"
  | "startups"
  | "startupDetail"
  | "analysisRun"
  | "dossier"
  | "opportunities";

export default function App() {
  const [activeView, setActiveView] = useState<ActiveView>("setup");
  const [ready, setReady] = useState<boolean | null>(null);
  const [selectedStartupId, setSelectedStartupId] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const checkReadiness = useCallback(async () => {
    try {
      const r = await getProductReadiness();
      setReady(r.ready);
      if (r.ready && activeView === "setup") {
        setActiveView("startups");
      }
    } catch {
      setReady(false);
    }
  }, [activeView]);

  useEffect(() => {
    checkReadiness();
  }, []);

  function navigateTo(view: string) {
    if (view === "setup" || view === "capabilities" || view === "startups" || view === "opportunities" || view === "startupDetail" || view === "analysisRun" || view === "dossier") {
      setActiveView(view);
    }
  }

  function handleSelectStartup(id: string) {
    setSelectedStartupId(id);
    setActiveView("startupDetail");
  }

  function handleRunCreated(runId: string) {
    setSelectedRunId(runId);
    setActiveView("analysisRun");
  }

  function handleViewDossier(runId: string) {
    setSelectedRunId(runId);
    setActiveView("dossier");
  }

  function handleBackFromStartup() {
    setSelectedStartupId(null);
    setActiveView("startups");
  }

  function handleBackFromRun() {
    if (selectedStartupId) {
      setActiveView("startupDetail");
    } else {
      setActiveView("startups");
    }
  }

  function handleBackFromDossier() {
    setActiveView("analysisRun");
  }

  return (
    <div className="app-shell">
      <header className="top-header">
        <div className="top-header-left">
          <h1 className="app-title" onClick={() => navigateTo("setup")}>
            NVIDIA Startup AI Radar
          </h1>
          <span className="app-badge">Product UI</span>
          {ready === true && <span className="status-dot ok" title="Product ready" />}
          {ready === false && <span className="status-dot bad" title="Product not ready" />}
          {ready === null && <span className="status-dot loading" title="Checking..." />}
        </div>
        <nav className="top-nav">
          <button
            type="button"
            className={`nav-btn ${activeView === "setup" ? "active" : ""}`}
            onClick={() => navigateTo("setup")}
          >
            Setup
          </button>
          <button
            type="button"
            className={`nav-btn ${activeView === "capabilities" ? "active" : ""}`}
            onClick={() => navigateTo("capabilities")}
          >
            Capabilities
          </button>
          <button
            type="button"
            className={`nav-btn ${activeView === "startups" || activeView === "startupDetail" ? "active" : ""}`}
            onClick={() => navigateTo("startups")}
          >
            Startups
          </button>
          <button
            type="button"
            className={`nav-btn ${activeView === "opportunities" ? "active" : ""}`}
            onClick={() => navigateTo("opportunities")}
          >
            Opportunities
          </button>
        </nav>
      </header>

      <main className="main-content">
        {activeView === "setup" && (
          <SetupReadinessView onNavigate={navigateTo} />
        )}

        {activeView === "capabilities" && <CapabilitiesView />}

        {activeView === "startups" && (
          <StartupListView onSelectStartup={handleSelectStartup} />
        )}

        {activeView === "startupDetail" && selectedStartupId && (
          <StartupDetailPanel
            startupId={selectedStartupId}
            onBack={handleBackFromStartup}
            onRunCreated={handleRunCreated}
          />
        )}

        {activeView === "analysisRun" && selectedRunId && (
          <AnalysisRunDetailView
            runId={selectedRunId}
            onBack={handleBackFromRun}
            onViewDossier={handleViewDossier}
          />
        )}

        {activeView === "dossier" && selectedRunId && (
          <DossierView
            runId={selectedRunId}
            onBack={handleBackFromDossier}
          />
        )}

        {activeView === "opportunities" && (
          <OpportunitiesView
            onSelectRun={handleRunCreated}
            onSelectStartup={handleSelectStartup}
          />
        )}
      </main>
    </div>
  );
}
