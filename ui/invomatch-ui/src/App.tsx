import { useState } from "react";
import { useAuthSession } from "./auth/useAuthSession";
import OperationalVisibilityPage from "./pages/OperationalVisibilityPage";
import RunDetailPage from "./pages/RunDetailPage";
import RunListPage from "./pages/RunListPage";
import UploadPage from "./pages/UploadPage";

const OPERATIONS_VIEW_METRICS_PERMISSION = "operations.view_metrics";

type ViewMode = "upload" | "list" | "detail" | "operations";

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>("upload");
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const {
    error: authSessionError,
    hasPermission,
    loading: authSessionLoading,
    reloadSession,
    status: authSessionStatus,
    user,
  } = useAuthSession();

  const canViewOperations =
    authSessionStatus === "authenticated" &&
    hasPermission(OPERATIONS_VIEW_METRICS_PERMISSION);
  const effectiveViewMode =
    viewMode === "operations" && !canViewOperations ? "list" : viewMode;

  function openRun(runId: string) {
    setSelectedRunId(runId);
    setViewMode("detail");
  }

  function goToRunList() {
    setViewMode("list");
  }

  function goToUpload() {
    setViewMode("upload");
  }

  function goToOperations() {
    if (!canViewOperations) {
      return;
    }

    setViewMode("operations");
  }

  function backToRunList() {
    setViewMode("list");
  }

  return (
    <div>
      <div style={{ padding: 20, borderBottom: "1px solid #444", marginBottom: 12 }}>
        <div style={{ marginBottom: 12 }}>
          <button onClick={goToUpload} style={{ marginRight: 8 }}>
            Upload
          </button>
          <button onClick={goToRunList} style={{ marginRight: 8 }}>
            Run List
          </button>
          {canViewOperations && (
            <button
              onClick={goToOperations}
              title="Backend-derived operations.view_metrics permission is present for the current session."
            >
              Admin Ops
            </button>
          )}
        </div>

        <div style={{ fontSize: 13 }}>
          <span style={{ marginRight: 12 }}>
            Session: {authSessionLoading ? "loading" : authSessionStatus}
          </span>

          {user && (
            <span style={{ marginRight: 12 }}>
              User: {user.username} / Tenant: {user.tenant_id}
            </span>
          )}

          {authSessionError && (
            <span style={{ color: "red", marginRight: 12 }}>
              {authSessionError}
            </span>
          )}

          <button
            disabled={authSessionLoading}
            onClick={() => {
              void reloadSession();
            }}
          >
            Refresh session
          </button>
        </div>
      </div>

      {effectiveViewMode === "upload" && (
        <UploadPage
          onOpenRun={openRun}
          onGoToRunList={goToRunList}
        />
      )}

      {effectiveViewMode === "list" && (
        <RunListPage onSelectRun={openRun} />
      )}

      {effectiveViewMode === "detail" && selectedRunId && (
        <RunDetailPage
          runId={selectedRunId}
          onBack={backToRunList}
        />
      )}

      {effectiveViewMode === "operations" && canViewOperations && (
        <OperationalVisibilityPage />
      )}
    </div>
  );
}

export default App;