import { useCallback, useEffect, useState } from "react";
import { useAuthSession } from "../auth/useAuthSession";
import ActionPanel from "../components/ActionPanel";
import ExportPanel from "../components/ExportPanel";
import ReviewPanel from "../components/ReviewPanel";
import { getRunView } from "../services/api";
import type { ApiError, RunViewResponse } from "../services/api";

const RUNS_READ_VIEW_PERMISSION = "runs.read_view";

type RunDetailPageProps = {
  runId: string;
  onBack: () => void;
};

function runDetailAccessMessage(
  status: string,
  sessionError: string | null,
  canReadRunView: boolean,
): string | null {
  if (status === "loading") {
    return "Run detail is waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Run detail is unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return sessionError ?? "Run detail is unavailable because the session could not be loaded.";
  }

  if (!canReadRunView) {
    return "Run detail is hidden because the current session does not include runs.read_view.";
  }

  return null;
}

function runDetailApiErrorMessage(err: unknown): string {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401) {
    return "Run detail access was denied because the backend did not authenticate the current request.";
  }

  if (apiError?.status === 403) {
    return "Run detail access was denied by backend authorization for runs.read_view.";
  }

  return apiError?.message ?? "Failed to load run detail.";
}

export default function RunDetailPage({ runId, onBack }: RunDetailPageProps) {
  const {
    status: sessionStatus,
    error: sessionError,
    hasPermission,
  } = useAuthSession();

  const [runView, setRunView] = useState<RunViewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const canReadRunView =
    sessionStatus === "authenticated" &&
    hasPermission(RUNS_READ_VIEW_PERMISSION);

  const loadRunView = useCallback(async () => {
    const accessMessage = runDetailAccessMessage(
      sessionStatus,
      sessionError,
      canReadRunView,
    );

    if (accessMessage) {
      setRunView(null);
      setLoading(sessionStatus === "loading");
      setError(sessionStatus === "loading" ? null : accessMessage);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await getRunView(runId);
      setRunView(response);
    } catch (err: unknown) {
      setRunView(null);
      setError(runDetailApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [canReadRunView, runId, sessionError, sessionStatus]);

  useEffect(() => {
    void loadRunView();
  }, [loadRunView]);

  return (
    <div style={{ padding: 20 }}>
      <button onClick={onBack} style={{ marginBottom: 16 }}>
        Back to Run List
      </button>

      <h2>Run Detail</h2>

      {loading && <p>Loading run detail...</p>}

      {error && (
        <div
          role="alert"
          style={{
            border: "1px solid #a33",
            color: "red",
            marginBottom: 16,
            padding: 12,
          }}
        >
          <strong>Run detail unavailable.</strong>
          <p style={{ marginBottom: 0 }}>{error}</p>
        </div>
      )}

      {!loading && !error && runView && (
        <>
          <div>
            <p>Run ID: {runView.run_id}</p>
            <p>Status: {runView.status}</p>
            <p>Created At: {runView.created_at}</p>
            <p>Updated At: {runView.updated_at}</p>
          </div>

          <div style={{ marginTop: 16 }}>
            <h3>Match Summary</h3>
            <p>Total Items: {runView.match_summary.total_items}</p>
            <p>Matched Items: {runView.match_summary.matched_items}</p>
            <p>Unmatched Items: {runView.match_summary.unmatched_items}</p>
            <p>Ambiguous Items: {runView.match_summary.ambiguous_items}</p>
          </div>

          <ReviewPanel reviewSummary={runView.review_summary} />

          <ExportPanel
            exportSummary={runView.export_summary}
            artifacts={runView.artifacts}
          />

          <ActionPanel
            runId={runView.run_id}
            onActionComplete={() => {
              void loadRunView();
            }}
          />
        </>
      )}
    </div>
  );
}
