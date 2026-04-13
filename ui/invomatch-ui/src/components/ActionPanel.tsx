import { useState } from "react";
import { executeRunAction } from "../services/api";
import type { ActionResponse, ApiError } from "../services/api";

type ActionPanelProps = {
  runId: string;
  onActionComplete: () => void;
};

export default function ActionPanel({ runId, onActionComplete }: ActionPanelProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ActionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleExportRun() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await executeRunAction(runId, {
        action_type: "export_run",
        note: "Triggered from EPIC 21 UI",
        payload: {
          format: "json",
        },
      });

      setResult(response);
      onActionComplete();
    } catch (err: unknown) {
      const apiError = err as Partial<ApiError>;
      setError(apiError?.message ?? "Action failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Actions</h3>

      <button onClick={handleExportRun} disabled={loading}>
        Export Run
      </button>

      {loading && <p>Executing action...</p>}

      {result && (
        <pre style={{ color: "green", whiteSpace: "pre-wrap", marginTop: 12 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

      {error && (
        <p style={{ color: "red", marginTop: 12 }}>
          {error}
        </p>
      )}
    </div>
  );
}