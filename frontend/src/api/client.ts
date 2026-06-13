export type JsonObject = Record<string, unknown>;

export type StartupInput = {
  startup_name: string;
  source_url?: string;
  profile?: JsonObject;
  evidence?: JsonObject[];
  [key: string]: unknown;
};

export type BriefResponse = {
  run_id: string;
  startup_name: string;
  brief_json: JsonObject;
  brief_markdown: string;
  run_report: JsonObject;
  answer_quality_eval: JsonObject | null;
  warnings: string[];
};

export type EvaluateResponse = {
  status: "PASS" | "WARN" | "FAIL" | string;
  metrics: JsonObject;
  gates: JsonObject[];
  failure_reasons: string[];
  warnings: string[];
};

export type RagStatusResponse = {
  backend: string;
  collection_name: string;
  vector_size: number;
  qdrant_url: string;
  qdrant_available: boolean;
  error: string | null;
};

export type ArtifactItem = {
  filename: string;
  path: string;
  size_bytes: number;
  modified_at: string;
};

export type ArtifactListResponse = {
  artifacts: ArtifactItem[];
  total: number;
};

export type HealthResponse = {
  status: string;
};

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

export async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
      ...init,
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new Error(`API offline or unreachable at ${API_BASE_URL}: ${detail}`);
  }

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : String(body);
    throw new Error(`API request failed (${response.status}): ${detail}`);
  }

  return body as T;
}

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health");
}

export function getRagStatus(): Promise<RagStatusResponse> {
  return requestJson<RagStatusResponse>("/rag/status");
}

export function createBrief(payload: {
  startup_name: string;
  profile: JsonObject;
  evidence: JsonObject[];
  source_url: string;
  use_rag: boolean;
  rag_backend: "local" | "qdrant";
  offline: boolean;
  run_answer_quality_eval: boolean;
}): Promise<BriefResponse> {
  return requestJson<BriefResponse>("/brief", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function evaluateBrief(
  startupName: string,
  briefJson: JsonObject,
): Promise<EvaluateResponse> {
  return requestJson<EvaluateResponse>("/brief/evaluate", {
    method: "POST",
    body: JSON.stringify({
      startup_name: startupName,
      brief_json: briefJson,
    }),
  });
}

export function listDemoArtifacts(path = ""): Promise<ArtifactListResponse> {
  const query = path ? `?path=${encodeURIComponent(path)}` : "";
  return requestJson<ArtifactListResponse>(`/demo/artifacts${query}`);
}
