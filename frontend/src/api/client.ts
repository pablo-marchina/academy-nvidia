export type JsonObject = Record<string, unknown>;

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
