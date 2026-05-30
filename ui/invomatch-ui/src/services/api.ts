const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const API_AUTH_TOKEN = import.meta.env.VITE_API_AUTH_TOKEN ?? "";

export type ApiError = {
  status: number;
  code: string;
  message: string;
  details?: unknown;
};

export type AuthSessionUser = {
  user_id: string;
  username: string;
  role: string;
  status: string;
  tenant_id: string;
  auth_source: string;
};

export type AuthSessionResponse = {
  user: AuthSessionUser;
  permissions: string[];
};

export type InputSubmissionResponse = {
  input_id: string;
  status: string;
  ingestion_batch_id?: string | null;
  run_id?: string | null;
  errors?: Array<Record<string, unknown>>;
};

export type RunListItem = {
  run_id: string;
  status: string;
  created_at?: string;
  updated_at?: string | null;
  match_count?: number;
  review_required_count?: number;
};

export type RunListResponse = {
  items: RunListItem[];
  total: number;
  limit: number;
  offset: number;
};

export type RunMatchSummary = {
  total_items: number;
  matched_items: number;
  unmatched_items: number;
  ambiguous_items: number;
};

export type RunReviewSummary = {
  status: string;
  total_items: number;
  open_items: number;
  resolved_items: number;
};

export type RunExportSummary = {
  status: string;
  artifact_count: number;
};

export type RunArtifactReference = {
  artifact_id: string;
  kind: string;
  file_name: string;
  media_type: string;
  size_bytes: number;
  created_at: string;
  download_url?: string | null;
};

export type RunViewResponse = {
  run_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  error?: Record<string, unknown> | null;
  match_summary: RunMatchSummary;
  review_summary: RunReviewSummary;
  export_summary: RunExportSummary;
  artifacts: RunArtifactReference[];
};

export type ReviewResponse = Record<string, unknown>;

export type ActionRequest = {
  action_type: string;
  target_id?: string | null;
  note?: string | null;
  payload?: Record<string, unknown>;
};

export type ActionResponse = {
  run_id: string;
  action_type: string;
  accepted: boolean;
  status: string;
  message?: string | null;
};

export type ExportResponse = Record<string, unknown>;

export type OperationalStatus = "healthy" | "degraded" | "attention_required";

export type OperationalAlertStatus = "clear" | "active";

export type OperationalAlertSeverity = "info" | "warning" | "critical";

export type OperationalRecommendedAction =
  | "none"
  | "inspect_startup_repair"
  | "inspect_terminal_failures"
  | "inspect_recovery_activity";

export type OperationalSignals = Record<string, number>;

export type OperationalMetricsResponse = {
  status: OperationalStatus;
  generated_at: string;
  signals: OperationalSignals;
  counters: Record<string, number>;
  decision_counts: Record<string, number>;
  reason_counts: Record<string, number>;
};

export type OperationalHealthSummaryResponse = {
  status: OperationalStatus;
  generated_at: string;
  summary: Record<string, string>;
  signals: OperationalSignals;
  recommended_action: OperationalRecommendedAction;
};

export type OperationalAlertResponse = {
  code: string;
  severity: OperationalAlertSeverity;
  message: string;
  recommended_action: OperationalRecommendedAction;
  signal: string;
  value: number;
};

export type OperationalAlertsResponse = {
  status: OperationalAlertStatus;
  generated_at: string;
  alerts: OperationalAlertResponse[];
};

export const OPERATIONAL_METRICS_RESPONSE_FIELDS = [
  "status",
  "generated_at",
  "signals",
  "counters",
  "decision_counts",
  "reason_counts",
] as const;

export const OPERATIONAL_HEALTH_SUMMARY_RESPONSE_FIELDS = [
  "status",
  "generated_at",
  "summary",
  "signals",
  "recommended_action",
] as const;

export const OPERATIONAL_ALERTS_RESPONSE_FIELDS = [
  "status",
  "generated_at",
  "alerts",
] as const;

export const OPERATIONAL_ALERT_RESPONSE_FIELDS = [
  "code",
  "severity",
  "message",
  "recommended_action",
  "signal",
  "value",
] as const;

async function parseJsonSafe(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function buildRequestHeaders(init?: RequestInit): Headers {
  const headers = new Headers(init?.headers);

  if (API_AUTH_TOKEN && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${API_AUTH_TOKEN}`);
  }

  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: buildRequestHeaders(init),
  });

  const body = await parseJsonSafe(response);

  if (!response.ok) {
    const errorBody =
      body && typeof body === "object" ? (body as Record<string, unknown>) : {};

    const error: ApiError = {
      status: response.status,
      code: String(errorBody.error_code ?? errorBody.code ?? "API_ERROR"),
      message: String(errorBody.message ?? `Request failed with status ${response.status}`),
      details: errorBody.details,
    };

    throw error;
  }

  return body as T;
}

export async function getAuthSession(): Promise<AuthSessionResponse> {
  return request<AuthSessionResponse>("/api/auth/session", {
    method: "GET",
  });
}

export async function submitJsonInput(
  payload: Record<string, unknown>,
): Promise<InputSubmissionResponse> {
  return request<InputSubmissionResponse>("/api/reconciliation/input/json", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function submitFileInput(file: File): Promise<InputSubmissionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<InputSubmissionResponse>("/api/reconciliation/input/file", {
    method: "POST",
    body: formData,
  });
}

export async function listRuns(): Promise<RunListResponse> {
  return request<RunListResponse>("/api/reconciliation/runs", {
    method: "GET",
  });
}

export async function getRunView(runId: string): Promise<RunViewResponse> {
  return request<RunViewResponse>(`/api/reconciliation/runs/${runId}/view`, {
    method: "GET",
  });
}

export async function getRunReview(runId: string): Promise<ReviewResponse> {
  return request<ReviewResponse>(`/api/reconciliation/runs/${runId}/review`, {
    method: "GET",
  });
}

export async function executeRunAction(
  runId: string,
  action: ActionRequest,
): Promise<ActionResponse> {
  return request<ActionResponse>(`/api/reconciliation/runs/${runId}/actions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(action),
  });
}

export async function getRunExport(runId: string): Promise<ExportResponse> {
  return request<ExportResponse>(`/api/reconciliation/runs/${runId}/export`, {
    method: "GET",
  });
}

/*
 * Operational visibility endpoints are admin-only integration surfaces.
 * Backend authorization through operations.view_metrics remains the source of truth.
 *
 * The frontend may hide or show navigation using backend-derived session
 * permissions, but it must not invent frontend-only roles or weaken backend
 * authorization on operational endpoints.
 */
export async function getOperationalMetrics(): Promise<OperationalMetricsResponse> {
  return request<OperationalMetricsResponse>("/api/operations/metrics", {
    method: "GET",
  });
}

export async function getOperationalHealthSummary(): Promise<OperationalHealthSummaryResponse> {
  return request<OperationalHealthSummaryResponse>("/api/operations/health-summary", {
    method: "GET",
  });
}

export async function getOperationalAlerts(): Promise<OperationalAlertsResponse> {
  return request<OperationalAlertsResponse>("/api/operations/alerts", {
    method: "GET",
  });
}

export type ReviewQueueRow = {
  match_id: string;
  status?: string | null;
  reason?: string | null;
  run_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  amount_summary?: string | null;
};

export type ReviewQueueResponse = {
  items: ReviewQueueRow[];
  total: number;
  limit?: number;
  offset?: number;
};

export async function listReviewQueue(): Promise<ReviewQueueResponse> {
  return request<ReviewQueueResponse>("/api/review/queue", {
    method: "GET",
  });
}
export type MatchDetailResponse = Record<string, unknown>;

export async function getReviewMatchDetail(matchId: string): Promise<MatchDetailResponse> {
const encodedMatchId = encodeURIComponent(matchId);
const path = "/api/review/matches/" + encodedMatchId + "/detail";

return request<MatchDetailResponse>(path, {
method: "GET",
});
}
