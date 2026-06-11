import { useEffect, useMemo, useState } from "react";

import {
  createBrief,
  evaluateBrief,
  getHealth,
  getRagStatus,
  listDemoArtifacts,
  type ArtifactListResponse,
  type BriefResponse,
  type HealthResponse,
  type JsonObject,
  type RagStatusResponse,
  type StartupInput,
} from "./api/client";
import { BriefViewer } from "./components/BriefViewer";
import { EvalStatusPanel } from "./components/EvalStatusPanel";
import { EvidencePanel } from "./components/EvidencePanel";
import { GapTechnologyTable } from "./components/GapTechnologyTable";
import { RagStatusBadge } from "./components/RagStatusBadge";
import { ScoreCards } from "./components/ScoreCards";
import { StartupInputForm } from "./components/StartupInputForm";
import { sampleStartupInput } from "./sampleStartupInput";

function prettyJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function isObject(value: unknown): value is JsonObject {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function parseStartupInput(inputText: string): StartupInput {
  let parsed: unknown;
  try {
    parsed = JSON.parse(inputText);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new Error(`Invalid JSON input: ${detail}`);
  }

  if (!isObject(parsed)) {
    throw new Error("Input must be a JSON object.");
  }
  if (typeof parsed.startup_name !== "string" || parsed.startup_name.trim() === "") {
    throw new Error("Input must include a non-empty startup_name.");
  }
  if (parsed.profile !== undefined && !isObject(parsed.profile)) {
    throw new Error("profile must be a JSON object when provided.");
  }
  if (parsed.evidence !== undefined && !Array.isArray(parsed.evidence)) {
    throw new Error("evidence must be an array when provided.");
  }

  return parsed as StartupInput;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export default function App() {
  const [inputText, setInputText] = useState(prettyJson(sampleStartupInput));
  const [offline, setOffline] = useState(true);
  const [useRag, setUseRag] = useState(false);
  const [ragBackend, setRagBackend] = useState<"local" | "qdrant">("local");
  const [runEvalWithBrief, setRunEvalWithBrief] = useState(false);

  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [ragStatus, setRagStatus] = useState<RagStatusResponse | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactListResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [ragError, setRagError] = useState<string | null>(null);

  const [briefResponse, setBriefResponse] = useState<BriefResponse | null>(null);
  const [evalResult, setEvalResult] = useState<JsonObject | null>(null);
  const [inputError, setInputError] = useState<string | null>(null);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [evalError, setEvalError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);

  const briefJson = briefResponse?.brief_json ?? null;
  const briefMarkdown = briefResponse?.brief_markdown ?? "";
  const warnings = briefResponse?.warnings ?? [];

  const currentStartupName = useMemo(() => {
    if (briefResponse?.startup_name) {
      return briefResponse.startup_name;
    }
    try {
      return parseStartupInput(inputText).startup_name;
    } catch {
      return "";
    }
  }, [briefResponse?.startup_name, inputText]);

  async function refreshRuntimeStatus() {
    setHealthError(null);
    setRagError(null);

    try {
      setHealth(await getHealth());
    } catch (error) {
      setHealth(null);
      setHealthError(errorMessage(error));
    }

    try {
      setRagStatus(await getRagStatus());
    } catch (error) {
      setRagStatus(null);
      setRagError(errorMessage(error));
    }

    try {
      setArtifacts(await listDemoArtifacts());
    } catch {
      setArtifacts(null);
    }
  }

  useEffect(() => {
    void refreshRuntimeStatus();
  }, []);

  function handleLoadExample() {
    setInputText(prettyJson(sampleStartupInput));
    setInputError(null);
    setGenerationError(null);
  }

  async function handleGenerateBrief() {
    setInputError(null);
    setGenerationError(null);
    setEvalError(null);

    let parsed: StartupInput;
    try {
      parsed = parseStartupInput(inputText);
    } catch (error) {
      setInputError(errorMessage(error));
      return;
    }

    setIsGenerating(true);
    try {
      const response = await createBrief({
        startup_name: parsed.startup_name,
        profile: parsed.profile || {},
        evidence: parsed.evidence || [],
        source_url:
          typeof parsed.source_url === "string" ? parsed.source_url : "https://example.com",
        use_rag: useRag,
        rag_backend: ragBackend,
        offline,
        run_answer_quality_eval: runEvalWithBrief,
      });
      setBriefResponse(response);
      setEvalResult(response.answer_quality_eval);
      await refreshRuntimeStatus();
    } catch (error) {
      setGenerationError(errorMessage(error));
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleEvaluateBrief() {
    if (!briefResponse?.brief_json) {
      setEvalError("Generate a brief before running evaluation.");
      return;
    }
    setEvalError(null);
    setIsEvaluating(true);
    try {
      const response = await evaluateBrief(currentStartupName, briefResponse.brief_json);
      setEvalResult(response as unknown as JsonObject);
    } catch (error) {
      setEvalError(errorMessage(error));
    } finally {
      setIsEvaluating(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">NVIDIA Startup AI Radar</p>
          <h1>Minimal Demo UI</h1>
          <p>
            Local interface for generating Startup Action Briefs from the existing
            FastAPI demo API.
          </p>
        </div>
        <div className="hero-meta">
          <span>API base</span>
          <strong>{import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}</strong>
        </div>
      </header>

      <div className="workspace-grid">
        <aside className="left-column">
          <RagStatusBadge
            health={health}
            ragStatus={ragStatus}
            artifacts={artifacts}
            healthError={healthError}
            ragError={ragError}
            onRefresh={refreshRuntimeStatus}
          />
          <StartupInputForm
            inputText={inputText}
            onInputTextChange={setInputText}
            offline={offline}
            onOfflineChange={setOffline}
            useRag={useRag}
            onUseRagChange={setUseRag}
            ragBackend={ragBackend}
            onRagBackendChange={setRagBackend}
            runEvalWithBrief={runEvalWithBrief}
            onRunEvalWithBriefChange={setRunEvalWithBrief}
            isGenerating={isGenerating}
            inputError={inputError}
            generationError={generationError}
            onLoadExample={handleLoadExample}
            onGenerate={handleGenerateBrief}
          />
          <EvalStatusPanel
            evalResult={evalResult}
            isEvaluating={isEvaluating}
            evalError={evalError}
            canEvaluate={!!briefResponse?.brief_json}
            onEvaluate={handleEvaluateBrief}
          />
        </aside>

        <section className="right-column">
          <ScoreCards
            briefJson={briefJson}
            runReport={(briefResponse?.run_report as JsonObject | undefined) || null}
          />
          <GapTechnologyTable
            gaps={briefJson?.diagnosed_gaps}
            technologies={briefJson?.nvidia_technology_candidates}
            recommendations={briefJson?.recommendations}
          />
          <EvidencePanel
            evidence={briefJson?.evidence_used}
            missingEvidence={briefJson?.missing_evidence}
            uncertainties={briefJson?.uncertainties}
            warnings={warnings}
          />
          <BriefViewer briefJson={briefJson} briefMarkdown={briefMarkdown} />
        </section>
      </div>
    </main>
  );
}
