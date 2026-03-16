let cachedBaseUrl: string | null = null;

export function getApiBaseUrl(): string {
  if (cachedBaseUrl) return cachedBaseUrl;

  const raw = import.meta.env.VITE_API_BASE_URL;
  if (!raw) {
    throw new Error("VITE_API_BASE_URL is not defined.");
  }
  cachedBaseUrl = raw.replace(/\/$/, "");
  return cachedBaseUrl;
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}${p}`;
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = apiUrl(path);
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    let detail: string;
    try {
      const j = JSON.parse(text);
      detail = j.detail ?? text;
    } catch {
      detail = text || res.statusText;
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
