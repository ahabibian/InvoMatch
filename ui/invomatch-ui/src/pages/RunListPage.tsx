import { useEffect, useState } from "react";
import { useAuthSession } from "../auth/useAuthSession";
import RunTable from "../components/RunTable";
import { listRuns } from "../services/api";
import type { ApiError, RunListItem } from "../services/api";

const RUNS_LIST_PERMISSION = "runs.list";

type RunListPageProps = {
  onSelectRun: (runId: string) => void;
};

function runListAccessMessage(
  status: string,
  sessionError: string | null,
  canListRuns: boolean,
): string | null {
  if (status === "loading") {
    return "Run list is waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Run list is unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return sessionError ?? "Run list is unavailable because the session could not be loaded.";
  }

  if (!canListRuns) {
    return "Run list is hidden because the current session does not include runs.list.";
  }

  return null;
}

function runListApiErrorMessage(err: unknown): string {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401) {
    return "Run list access was denied because the backend did not authenticate the current request.";
  }

  if (apiError?.status === 403) {
    return "Run list access was denied by backend authorization for runs.list.";
  }

  return apiError?.message ?? "Failed to load runs.";
}

export default function RunListPage({ onSelectRun }: RunListPageProps) {
  const {
    status: sessionStatus,
    error: sessionError,
    hasPermission,
  } = useAuthSession();

  const [items, setItems] = useState<RunListItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const canListRuns =
    sessionStatus === "authenticated" &&
    hasPermission(RUNS_LIST_PERMISSION);

  useEffect(() => {
    const accessMessage = runListAccessMessage(
      sessionStatus,
      sessionError,
      canListRuns,
    );

    if (accessMessage) {
      setItems([]);
      setTotal(0);
      setLoading(sessionStatus === "loading");
      setError(sessionStatus === "loading" ? null : accessMessage);
      return;
    }

    async function loadRuns() {
      setLoading(true);
      setError(null);

      try {
        const response = await listRuns();
        setItems(response.items);
        setTotal(response.total);
      } catch (err: unknown) {
        setItems([]);
        setTotal(0);
        setError(runListApiErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }

    void loadRuns();
  }, [canListRuns, sessionError, sessionStatus]);

  return (
    <div style={{ padding: 20 }}>
      <h2>Run List</h2>

      {loading && <p>Loading runs...</p>}

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
          <strong>Run list unavailable.</strong>
          <p style={{ marginBottom: 0 }}>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          <p>Total runs: {total}</p>
          <RunTable items={items} onSelectRun={onSelectRun} />
        </>
      )}
    </div>
  );
}
