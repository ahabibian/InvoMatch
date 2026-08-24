import { useCallback, useEffect, useState } from "react";
import { useAuthSession } from "../auth/useAuthSession";
import { listReviewQueue } from "../services/api";
import type { ApiError, ReviewQueueRow } from "../services/api";

const RUNS_READ_REVIEW_PERMISSION = "runs.read_review";

type ReviewQueuePageProps = {
  onOpenMatch: (matchId: string) => void;
};

function reviewQueueAccessMessage(
  status: string,
  sessionError: string | null,
  canReadReview: boolean,
): string | null {
  if (status === "loading") {
    return "Review Queue is waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Review Queue is unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return sessionError ?? "Review Queue is unavailable because the session could not be loaded.";
  }

  if (!canReadReview) {
    return "Review Queue is hidden because the current session does not include runs.read_review.";
  }

  return null;
}

function reviewQueueApiErrorMessage(err: unknown): string {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401) {
    return "Review Queue access was denied because the backend did not authenticate the current request.";
  }

  if (apiError?.status === 403) {
    return "Review Queue access was denied by backend authorization for runs.read_review.";
  }

  if (apiError?.status === 404) {
    return "Review Queue endpoint is unavailable. Backend GET /api/review/queue is not reachable from the frontend.";
  }

  return apiError?.message ?? "Failed to load Review Queue.";
}

function safeDisplay(value: string | null | undefined): string {
  return value && value.trim().length > 0 ? value : "Not provided by backend";
}

export default function ReviewQueuePage({ onOpenMatch }: ReviewQueuePageProps) {
  const {
    status: sessionStatus,
    error: sessionError,
    hasPermission,
  } = useAuthSession();

  const [rows, setRows] = useState<ReviewQueueRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const canReadReview =
    sessionStatus === "authenticated" &&
    hasPermission(RUNS_READ_REVIEW_PERMISSION);

  const loadReviewQueue = useCallback(async () => {
    const accessMessage = reviewQueueAccessMessage(
      sessionStatus,
      sessionError,
      canReadReview,
    );

    if (accessMessage) {
      setRows([]);
      setLoading(sessionStatus === "loading");
      setError(sessionStatus === "loading" ? null : accessMessage);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await listReviewQueue();
      setRows(response);
    } catch (err: unknown) {
      setRows([]);
      setError(reviewQueueApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [canReadReview, sessionError, sessionStatus]);

  useEffect(() => {
    void loadReviewQueue();
  }, [loadReviewQueue]);

  return (
    <div style={{ padding: 20 }}>
      <h2>Review Queue</h2>

      <p style={{ color: "#555", maxWidth: 760 }}>
        This surface renders backend-owned Review Queue rows only. It does not synthesize rows,
        calculate confidence, or pass Match Detail payload data.
      </p>

      <button
        disabled={loading}
        onClick={() => {
          void loadReviewQueue();
        }}
        style={{ marginBottom: 16 }}
      >
        Refresh Review Queue
      </button>

      {loading && <p>Loading Review Queue...</p>}

      {error && (
        <div
          role="alert"
          style={{ border: "1px solid #a33", color: "red", marginBottom: 16, padding: 12 }}
        >
          <strong>Review Queue unavailable.</strong>
          <p style={{ marginBottom: 0 }}>{error}</p>
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <div style={{ border: "1px solid #aaa", marginBottom: 16, padding: 12 }}>
          No backend-owned Review Queue rows were returned.
        </div>
      )}

      {!loading && !error && rows.length > 0 && (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              <th style={{ borderBottom: "1px solid #777", textAlign: "left", padding: 8 }}>Match ID</th>
              <th style={{ borderBottom: "1px solid #777", textAlign: "left", padding: 8 }}>Status</th>
              <th style={{ borderBottom: "1px solid #777", textAlign: "left", padding: 8 }}>Reason</th>
              <th style={{ borderBottom: "1px solid #777", textAlign: "left", padding: 8 }}>Run ID</th>
              <th style={{ borderBottom: "1px solid #777", textAlign: "left", padding: 8 }}>Amount Summary</th>
              <th style={{ borderBottom: "1px solid #777", textAlign: "left", padding: 8 }}>Handoff</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.case_id}>
                <td style={{ borderBottom: "1px solid #ddd", padding: 8 }}>{safeDisplay(row.match_id)}</td>
                <td style={{ borderBottom: "1px solid #ddd", padding: 8 }}>{safeDisplay(row.status)}</td>
                <td style={{ borderBottom: "1px solid #ddd", padding: 8 }}>{safeDisplay(row.reason_code)}</td>
                <td style={{ borderBottom: "1px solid #ddd", padding: 8 }}>{safeDisplay(row.run_id)}</td>
                <td style={{ borderBottom: "1px solid #ddd", padding: 8 }}>Not provided by backend</td>
                <td style={{ borderBottom: "1px solid #ddd", padding: 8 }}>
                  <button
                    disabled={!row.match_id}
                    onClick={() => {
                      if (row.match_id) {
                        onOpenMatch(row.match_id);
                      }
                    }}
                    title="Only match_id is passed across the Review Queue to Match Detail handoff boundary."
                  >
                    Open Match
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && !error && rows.length > 0 && (
        <p style={{ color: "#555", marginTop: 12 }}>
          Handoff boundary: only match_id is passed. Match Detail loading is not validated
          by this Review Queue surface.
        </p>
      )}
    </div>
  );
}
