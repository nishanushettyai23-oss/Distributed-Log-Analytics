const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    ...options
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Cloud analytics API request failed");
  }
  return payload;
}

export function reportUrl(format: "pdf" | "xlsx" | "csv") {
  return `${API_BASE}/api/reports/${format}`;
}
