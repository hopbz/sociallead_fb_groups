const DEFAULT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';
const BUILD_API_TOKEN = import.meta.env.VITE_API_TOKEN || '';

export const API_BASE_STORAGE_KEY = 'sociallead_fb_api_base_url';
export const API_TOKEN_STORAGE_KEY = 'sociallead_fb_api_token';

export function getApiBaseUrl() {
  return localStorage.getItem(API_BASE_STORAGE_KEY) || DEFAULT_API_BASE_URL;
}

export function getApiToken() {
  return localStorage.getItem(API_TOKEN_STORAGE_KEY) || BUILD_API_TOKEN;
}

export function saveApiConnection(baseUrl: string, token: string) {
  localStorage.setItem(API_BASE_STORAGE_KEY, baseUrl.replace(/\/$/, ''));
  localStorage.setItem(API_TOKEN_STORAGE_KEY, token.trim());
}

export function clearApiConnection() {
  localStorage.removeItem(API_TOKEN_STORAGE_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Token': getApiToken(),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export type GroupSource = { id: string; name: string; url: string; is_active: boolean; note?: string | null; privacy?: 'public' | 'private' | string | null; created_at: string; updated_at: string };
export type Keyword = { id: string; keyword: string; is_active: boolean; created_at: string };
export type Post = { id: string; group_url: string; group_name?: string | null; post_id?: string | null; post_url?: string | null; author?: string | null; content: string; matched_keywords?: string | null; engine: string; scraped_at: string; created_at: string };
export type Run = { id: string; engine: string; status: string; started_at: string; finished_at?: string | null; groups_total: number; groups_success: number; groups_failed: number; posts_seen: number; posts_inserted: number; posts_matched: number; message?: string | null };
export type ErrorLog = { id: string; run_id?: string | null; group_url?: string | null; engine?: string | null; error_message: string; screenshot_path?: string | null; created_at: string };
export type Dashboard = { groups_total: number; groups_active: number; keywords_total: number; posts_total: number; posts_today: number; runs_total: number; errors_total: number; last_run?: Run | null; recent_posts: Post[]; recent_runs: Run[]; daily_posts: { label: string; value: number }[] };
export type EngineName = 'playwright' | 'seleniumbase' | 'cdp_playwright';
export type RuntimeSettings = { default_engine: EngineName; headless: boolean; login_wait_timeout_seconds: number; facebook_latest_sorting: boolean; max_scrolls_per_group: number; max_posts_per_group: number; retry_times: number; scheduler_enabled: boolean; scheduler_interval_minutes: number; telegram_enabled: boolean; google_sheets_enabled: boolean };
export type ScanResponse = { run_id: string; status: string; engine: EngineName; groups_total: number; groups_success: number; groups_failed: number; posts_seen: number; posts_inserted: number; posts_matched: number; errors: string[] };
export type LoginStatus = { engine: EngineName; logged_in: boolean; profile_dir: string; storage_state_file?: string | null };

export const api = {
  health: () => request<{ ok: boolean; app: string }>('/api/v1/health'),
  dashboard: () => request<Dashboard>('/api/v1/dashboard'),
  groups: () => request<GroupSource[]>('/api/v1/groups'),
  createGroup: (payload: { name: string; url: string; is_active?: boolean; note?: string }) => request<GroupSource>('/api/v1/groups', { method: 'POST', body: JSON.stringify(payload) }),
  refreshGroupMetadata: () => request<GroupSource[]>('/api/v1/groups/refresh-metadata', { method: 'POST' }),
  updateGroup: (id: string, payload: Partial<{ name: string; url: string; is_active: boolean; note: string }>) => request<GroupSource>(`/api/v1/groups/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deleteGroup: (id: string) => request<{ ok: boolean }>(`/api/v1/groups/${id}`, { method: 'DELETE' }),
  keywords: () => request<Keyword[]>('/api/v1/keywords'),
  createKeyword: (payload: { keyword: string; is_active?: boolean }) => request<Keyword>('/api/v1/keywords', { method: 'POST', body: JSON.stringify(payload) }),
  toggleKeyword: (id: string, active: boolean) => request<Keyword>(`/api/v1/keywords/${id}?is_active=${active}`, { method: 'PATCH' }),
  deleteKeyword: (id: string) => request<{ ok: boolean }>(`/api/v1/keywords/${id}`, { method: 'DELETE' }),
  posts: (q = '') => request<Post[]>(`/api/v1/posts?limit=100${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  runs: () => request<Run[]>('/api/v1/runs?limit=50'),
  errors: () => request<ErrorLog[]>('/api/v1/errors?limit=50'),
  settings: () => request<RuntimeSettings>('/api/v1/settings'),
  loginStatus: (engine: EngineName) => request<LoginStatus>(`/api/v1/login-status/${engine}`),
  login: (engine: EngineName) => request<LoginStatus & { ok: boolean; message: string }>(`/api/v1/login/${engine}`, { method: 'POST' }),
  scan: (payload: { engine?: EngineName; max_scrolls?: number; max_posts_per_group?: number; send_telegram?: boolean; write_google_sheets?: boolean }) => request<ScanResponse>('/api/v1/scan-groups', { method: 'POST', body: JSON.stringify(payload) }),
};
