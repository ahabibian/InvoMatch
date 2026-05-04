import { useState } from "react";
import OperationalVisibilityPage from "./pages/OperationalVisibilityPage";
import RunDetailPage from "./pages/RunDetailPage";
import RunListPage from "./pages/RunListPage";
import UploadPage from "./pages/UploadPage";

type ViewMode = "upload" | "list" | "detail" | "operations";

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>("upload");
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

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
    setViewMode("operations");
  }

  function backToRunList() {
    setViewMode("list");
  }

  return (
    <div>
      <div style={{ padding: 20, borderBottom: "1px solid #444", marginBottom: 12 }}>
        <button onClick={goToUpload} style={{ marginRight: 8 }}>
          Upload
        </button>
        <button onClick={goToRunList} style={{ marginRight: 8 }}>
          Run List
        </button>
        {/*
          Current UI has no authenticated user/session/role/permission context.
          Do not add fake frontend RBAC here. Backend operations.view_metrics
          authorization remains the source of truth until real frontend auth
          primitives exist.
        */}
        <button
          onClick={goToOperations}
          title="Admin-only backend surface. Frontend role-aware navigation is not available yet."
        >
          Admin Ops
        </button>
      </div>

      {viewMode === "upload" && (
        <UploadPage
          onOpenRun={openRun}
          onGoToRunList={goToRunList}
        />
      )}

      {viewMode === "list" && (
        <RunListPage onSelectRun={openRun} />
      )}

      {viewMode === "detail" && selectedRunId && (
        <RunDetailPage
          runId={selectedRunId}
          onBack={backToRunList}
        />
      )}

      {viewMode === "operations" && (
        <OperationalVisibilityPage />
      )}
    </div>
  );
}

export default App;