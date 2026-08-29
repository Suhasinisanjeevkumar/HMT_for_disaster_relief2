import type {
  AlertListResponse,
  ClaimDetail,
  ClaimFilters,
  ClaimListResponse,
  CountItem,
  FeedHealth,
  MapPoint,
  OverviewStats,
  TimelinePoint,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { "content-type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError("Could not reach the HMT API. Is the backend running?", 0);
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      // response body wasn't JSON -- keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

function toQuery<T extends object>(params: T): string {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params as Record<string, unknown>)) {
    if (v !== undefined && v !== "") usp.set(k, String(v));
  }
  const s = usp.toString();
  return s ? `?${s}` : "";
}

export const api = {
  analyzeClaim: (text: string, source = "manual") =>
    request<ClaimDetail>("/api/claims", {
      method: "POST",
      body: JSON.stringify({ text, source }),
    }),

  listClaims: (filters: ClaimFilters = {}) =>
    request<ClaimListResponse>(`/api/claims${toQuery(filters)}`),

  getClaim: (id: number) => request<ClaimDetail>(`/api/claims/${id}`),

  statsOverview: () => request<OverviewStats>("/api/stats/overview"),
  statsDisasterTypes: () => request<CountItem[]>("/api/stats/disaster-types"),
  statsLocations: (by: "state" | "city" = "state", limit = 10) =>
    request<CountItem[]>(`/api/stats/locations${toQuery({ by, limit })}`),
  statsTimeline: () => request<TimelinePoint[]>("/api/stats/timeline"),

  mapClaims: (filters: { disaster_type?: string; priority?: string } = {}) =>
    request<MapPoint[]>(`/api/map/claims${toQuery(filters)}`),

  listAlerts: (filters: { acknowledged?: boolean; level?: string } = {}) =>
    request<AlertListResponse>(
      `/api/alerts${toQuery({
        acknowledged: filters.acknowledged === undefined ? undefined : String(filters.acknowledged),
        level: filters.level,
      })}`
    ),
  acknowledgeAlert: (id: number) =>
    request(`/api/alerts/${id}/acknowledge`, { method: "PATCH" }),

  feedStatus: () => request<FeedHealth[]>("/api/feeds/status"),
};
