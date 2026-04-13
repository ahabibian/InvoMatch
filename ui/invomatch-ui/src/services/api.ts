const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export type ApiError = {
  status: number;
  code: string;
  message: string;
  details?: unknown;
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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
    },
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