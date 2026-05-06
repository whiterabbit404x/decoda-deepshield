import {
  type Alert,
  type AnalyzeDetectionResponse,
  type EvidenceUploadResponse,
  type HealthResponse,
  type Incident
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEFAULT_TIMEOUT_MS = 12_000;

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function fetchJson<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: "no-store",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers
      }
    });

    if (!response.ok) {
      const message = await response.text();
      throw new ApiError(message || `Request failed: ${response.status}`, response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out", 408);
    }

    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError("Unable to reach DeepShield API. Please try again.");
  } finally {
    clearTimeout(timeoutId);
  }
}

export const getHealth = () => fetchJson<HealthResponse>("/health");
export const getAlerts = () => fetchJson<Alert[]>("/alerts");
export const getIncidents = () => fetchJson<Incident[]>("/incidents");

export function uploadEvidence(fileName: string, payload: unknown) {
  return fetchJson<EvidenceUploadResponse>("/evidence/upload", {
    method: "POST",
    body: JSON.stringify({ file_name: fileName, payload })
  });
}

export function analyzeDetections(content: string) {
  return fetchJson<AnalyzeDetectionResponse>("/detections/analyze", {
    method: "POST",
    body: JSON.stringify({ content })
  });
}
