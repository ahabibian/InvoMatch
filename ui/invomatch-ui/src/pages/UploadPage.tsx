import { useState } from "react";
import { submitJsonInput } from "../services/api";
import type { ApiError } from "../services/api";

type UploadPageProps = {
  onOpenRun: (runId: string) => void;
  onGoToRunList: () => void;
};

export default function UploadPage({ onOpenRun, onGoToRunList }: UploadPageProps) {
  const [jsonInput, setJsonInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRunId, setLastRunId] = useState<string | null>(null);

  async function handleJsonSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);
    setLastRunId(null);

    try {
      const parsed = JSON.parse(jsonInput);
      const res = await submitJsonInput(parsed);
      setResult(JSON.stringify(res, null, 2));

      if (res.run_id) {
        setLastRunId(res.run_id);
      }
    } catch (err: unknown) {
      const apiError = err as Partial<ApiError>;
      if (apiError?.message) {
        setError(apiError.message);
      } else {
        setError("Invalid JSON input");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleFileSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (!file) {
        setError("No file selected");
        return;
      }

      setResult(`File selected: ${file.name}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <div style={{ marginBottom: 16 }}>
        <button onClick={onGoToRunList}>Go to Run List</button>
      </div>

      <h2>Upload Input</h2>

      <div>
        <h3>JSON Input</h3>
        <textarea
          rows={10}
          cols={60}
          value={jsonInput}
          onChange={(e) => setJsonInput(e.target.value)}
        />
        <br />
        <button onClick={handleJsonSubmit} disabled={loading}>
          Submit JSON
        </button>
      </div>

      <hr />

      <div>
        <h3>File Upload</h3>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <br />
        <button onClick={handleFileSubmit} disabled={loading || !file}>
          Upload File
        </button>
      </div>

      <hr />

      {loading && <p>Processing...</p>}
      {result && <pre style={{ color: "green", whiteSpace: "pre-wrap" }}>{result}</pre>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {lastRunId && (
        <div style={{ marginTop: 16 }}>
          <button onClick={() => onOpenRun(lastRunId)}>
            Open Created Run
          </button>
        </div>
      )}
    </div>
  );
}