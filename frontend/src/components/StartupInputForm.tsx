type StartupInputFormProps = {
  inputText: string;
  onInputTextChange: (value: string) => void;
  offline: boolean;
  onOfflineChange: (value: boolean) => void;
  useRag: boolean;
  onUseRagChange: (value: boolean) => void;
  ragBackend: "local" | "qdrant";
  onRagBackendChange: (value: "local" | "qdrant") => void;
  runEvalWithBrief: boolean;
  onRunEvalWithBriefChange: (value: boolean) => void;
  isGenerating: boolean;
  inputError: string | null;
  generationError: string | null;
  onLoadExample: () => void;
  onGenerate: () => void;
};

export function StartupInputForm({
  inputText,
  onInputTextChange,
  offline,
  onOfflineChange,
  useRag,
  onUseRagChange,
  ragBackend,
  onRagBackendChange,
  runEvalWithBrief,
  onRunEvalWithBriefChange,
  isGenerating,
  inputError,
  generationError,
  onLoadExample,
  onGenerate,
}: StartupInputFormProps) {
  return (
    <section className="panel input-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Startup input</p>
          <h2>Demo payload</h2>
        </div>
        <button type="button" className="secondary-button" onClick={onLoadExample}>
          Load example
        </button>
      </div>

      <textarea
        value={inputText}
        onChange={(event) => onInputTextChange(event.target.value)}
        spellCheck={false}
        aria-label="Startup input JSON"
      />

      <div className="controls-grid">
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={offline}
            onChange={(event) => onOfflineChange(event.target.checked)}
          />
          Offline mode
        </label>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={useRag}
            onChange={(event) => onUseRagChange(event.target.checked)}
          />
          Use RAG
        </label>
        <label className="field-row">
          RAG backend
          <select
            value={ragBackend}
            disabled={!useRag || offline}
            onChange={(event) => onRagBackendChange(event.target.value as "local" | "qdrant")}
          >
            <option value="local">local</option>
            <option value="qdrant">qdrant</option>
          </select>
        </label>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={runEvalWithBrief}
            onChange={(event) => onRunEvalWithBriefChange(event.target.checked)}
          />
          Evaluate during generation
        </label>
      </div>

      {inputError ? <div className="message error-message">{inputError}</div> : null}
      {generationError ? <div className="message error-message">{generationError}</div> : null}

      <button
        type="button"
        className="primary-button"
        onClick={onGenerate}
        disabled={isGenerating}
      >
        {isGenerating ? "Generating..." : "Generate Startup Action Brief"}
      </button>
    </section>
  );
}
