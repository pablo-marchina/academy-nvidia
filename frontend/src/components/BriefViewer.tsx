import type { JsonObject } from "../api/client";

type BriefViewerProps = {
  briefJson: JsonObject | null;
  briefMarkdown: string;
};

type BriefSection = {
  title?: unknown;
  content?: unknown;
};

function sectionsFromBrief(briefJson: JsonObject | null): BriefSection[] {
  const sections = briefJson?.sections;
  if (!Array.isArray(sections)) {
    return [];
  }
  return sections.filter((section): section is BriefSection => {
    return !!section && typeof section === "object";
  });
}

export function BriefViewer({ briefJson, briefMarkdown }: BriefViewerProps) {
  const sections = sectionsFromBrief(briefJson);

  return (
    <section className="panel brief-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Startup Action Brief</p>
          <h2>{briefJson?.startup_name ? String(briefJson.startup_name) : "No brief generated"}</h2>
        </div>
      </div>

      {!briefJson ? (
        <p className="empty-state">Generate a brief to see the structured output here.</p>
      ) : (
        <>
          <div className="section-grid">
            {sections.map((section, index) => (
              <article className="brief-section" key={`${String(section.title)}-${index}`}>
                <h3>{String(section.title || "Untitled section")}</h3>
                <p>{String(section.content || "")}</p>
              </article>
            ))}
          </div>

          <details className="markdown-details" open>
            <summary>Markdown output</summary>
            <pre>{briefMarkdown}</pre>
          </details>
        </>
      )}
    </section>
  );
}
