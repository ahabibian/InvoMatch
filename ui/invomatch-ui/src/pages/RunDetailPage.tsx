import { useCallback, useEffect, useState } from "react";
import ActionPanel from "../components/ActionPanel";
import ExportPanel from "../components/ExportPanel";
import ReviewPanel from "../components/ReviewPanel";
import { getRunView } from "../services/api";
import type { ApiError, RunViewResponse } from "../services/api";

type RunDetailPageProps = {
  runId: string;
  onBack: () => void;
};

export default function RunDetailPage({ runId, onBack }: RunDetailPageProps) {
  const [runView, setRunView] = useState<RunViewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRunView = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getRunView(runId);
      setRunView(response);
    } catch (err: unknown) {
      const apiError = err as Partial<ApiError>;
      setError(apiError?.message ?? "Failed to load run detail");
    } finally {
      setLoading(false);
    }
  }, [runId]);

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
      {error && <p style={{ color: "red" }}>{error}</p>}

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