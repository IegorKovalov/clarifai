import type { AdminStats, IngestResponse, TenantInfo } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/api';

export const API_BASE = BASE_URL;
export const WS_BASE = WS_URL;

async function apiFetch<T>(
  path: string,
  apiKey: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'X-API-Key': apiKey,
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function fetchStats(apiKey: string): Promise<AdminStats> {
  return apiFetch<AdminStats>('/admin/stats', apiKey);
}

export async function fetchTenantInfo(apiKey: string): Promise<TenantInfo> {
  return apiFetch<TenantInfo>('/tenants/me', apiKey);
}

export async function ingestFile(apiKey: string, file: File): Promise<IngestResponse> {
  const form = new FormData();
  form.append('file', file);
  return apiFetch<IngestResponse>('/ingest/file', apiKey, {
    method: 'POST',
    body: form,
  });
}

export async function ingestUrl(apiKey: string, url: string): Promise<IngestResponse> {
  return apiFetch<IngestResponse>('/ingest/url', apiKey, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
}

export async function submitFeedback(
  apiKey: string,
  sessionId: string,
  feedback: 'thumbs_up' | 'thumbs_down',
): Promise<void> {
  await apiFetch<{ status: string }>(`/admin/feedback/${sessionId}`, apiKey, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback }),
  });
}

export function buildWsUrl(apiKey: string, sessionId: string): string {
  return `${WS_BASE}/chat/ws/${sessionId}?api_key=${encodeURIComponent(apiKey)}`;
}
