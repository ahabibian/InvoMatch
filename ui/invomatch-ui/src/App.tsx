import { useState } from "react";
import RunDetailPage from "./pages/RunDetailPage";
import RunListPage from "./pages/RunListPage";
import UploadPage from "./pages/UploadPage";

type ViewMode = "upload" | "list" | "detail";

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

  function backToRunList() {
    setViewMode("list");
  }

  return (
    <div>
      <div style={{ padding: 20, borderBottom: "1px solid #444", marginBottom: 12 }}>
        <button onClick={goToUpload} style={{ marginRight: 8 }}>
          Upload
        </button>
        <button onClick={goToRunList}>
          Run List
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
    </div>
  );
}

export default App;