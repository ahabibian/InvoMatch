import { useState } from "react";
import { useAuthSession } from "../auth/useAuthSession";
import { executeRunAction } from "../services/api";
import type { ActionResponse, ApiError } from "../services/api";

const ACTIONS_EXPORT_RUN_PERMISSION = "actions.export_run";

type ActionPanelProps = {
  runId: string;
  onActionComplete: () => void;
};

function actionControlMessage(
  status: string,
  error: string | null,
  canExportRun: boolean,
): string | null {
  if (status === "loading") {
    return "Action controls are waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Action controls are unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return error ?? "Action controls are unavailable because the session could not be loaded.";
  }

  if (!canExportRun) {
    return "Export action is unavailable because the current session does not include actions.export_run.";
  }

  return null;
}

export default function ActionPanel({ runId, onActionComplete }: ActionPanelProps) {
  const { status, error: sessionError, hasPermission } = useAuthSession();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ActionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canExportRun =
    status === "authenticated" &&
    hasPermission(ACTIONS_EXPORT_RUN_PERMISSION);

  const controlMessage = actionControlMessage(status, sessionError, canExportRun);

  async function handleExportRun() {
    if (!canExportRun) {
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await executeRunAction(runId, {
        action_type: "export_run",
        note: "Triggered from permission-aware product UI",
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

      <button onClick={handleExportRun} disabled={loading || !canExportRun}>
        Export Run
      </button>

      {controlMessage && (
        <p style={{ color: "#555", marginTop: 8 }}>
          {controlMessage}
        </p>
      )}

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