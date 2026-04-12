const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export type ApiError = {
  status: number;
  code: string;
  message: string;
  details?: unknown;
};

export type InputSubmissionResponse = {
  run_id: string;
  status: string;
};

export type RunListItem = {
  run_id: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  summary?: Record<string, unknown>;
};

export type RunViewResponse = {
  run: Record<string, unknown>;
  match_summary?: Record<string, unknown>;
  review_summary?: Record<string, unknown>;
  export_summary?: Record<string, unknown>;
};

export type ReviewResponse = {
  items: Array<Record<string, unknown>>;
};

export type ActionRequest = {
  action_type: string;
  payload?: Record<string, unknown>;
};

export type ActionResponse = {
  status: string;
  reason?: string;
};

export type ExportResponse = {
  ready: boolean;
  artifacts?: Array<Record<string, unknown>>;
};

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
  const response = await fetch(${API_BASE_URL}src\services\api.ts, {
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
      message: String(errorBody.message ?? "Request failed"),
      details: errorBody.details,
    };

    throw error;
  }

  return body as T;
}

export async function submitJsonInput(
  payload: Record<string, unknown>,
): Promise<InputSubmissionResponse> {
  return request<InputSubmissionResponse>("/input/json", {
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

  return request<InputSubmissionResponse>("/input/file", {
    method: "POST",
    body: formData,
  });
}

export async function listRuns(): Promise<RunListItem[]> {
  return request<RunListItem[]>("/runs", {
    method: "GET",
  });
}

export async function getRunView(runId: string): Promise<RunViewResponse> {
  return request<RunViewResponse>(/api/reconciliation/runs//view, {
    method: "GET",
  });
}

export async function getRunReview(runId: string): Promise<ReviewResponse> {
  return request<ReviewResponse>(/runs//review, {
    method: "GET",
  });
}

export async function executeRunAction(
  runId: string,
  action: ActionRequest,
): Promise<ActionResponse> {
  return request<ActionResponse>(/runs//actions, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(action),
  });
}

export async function getRunExport(runId: string): Promise<ExportResponse> {
  return request<ExportResponse>(/runs//export, {
    method: "GET",
  });
}