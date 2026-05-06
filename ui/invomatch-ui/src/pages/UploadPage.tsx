import { useState } from "react";
import { useAuthSession } from "../auth/useAuthSession";
import { submitFileInput, submitJsonInput } from "../services/api";
import type { ApiError } from "../services/api";

const INPUT_SUBMIT_PERMISSION = "input.submit";

type UploadPageProps = {
  onOpenRun: (runId: string) => void;
  onGoToRunList: () => void;
};

function inputAccessMessage(
  status: string,
  sessionError: string | null,
  canSubmitInput: boolean,
): string | null {
  if (status === "loading") {
    return "Input submission is waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Input submission is unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return sessionError ?? "Input submission is unavailable because the session could not be loaded.";
  }

  if (!canSubmitInput) {
    return "Input submission is hidden because the current session does not include input.submit.";
  }

  return null;
}

function inputSubmissionApiErrorMessage(err: unknown): string {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401) {
    return "Input submission failed because the current session is not authenticated.";
  }

  if (apiError?.status === 403) {
    return "Input submission was denied by backend authorization for input.submit.";
  }

  return apiError?.message ?? "Input submission failed.";
}

export default function UploadPage({ onOpenRun, onGoToRunList }: UploadPageProps) {
  const [jsonInput, setJsonInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRunId, setLastRunId] = useState<string | null>(null);
  const {
    status: sessionStatus,
    error: sessionError,
    hasPermission,
  } = useAuthSession();

  const canSubmitInput =
    sessionStatus === "authenticated" &&
    hasPermission(INPUT_SUBMIT_PERMISSION);

  const accessMessage = inputAccessMessage(
    sessionStatus,
    sessionError,
    canSubmitInput,
  );

  const controlsDisabled = loading || !canSubmitInput;

  async function handleJsonSubmit() {
    if (!canSubmitInput) {
      setError(accessMessage ?? "Input submission is unavailable.");
      return;
    }

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
      if (err instanceof SyntaxError) {
        setError("Invalid JSON input.");
      } else {
        setError(inputSubmissionApiErrorMessage(err));
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleFileSubmit() {
    if (!canSubmitInput) {
      setError(accessMessage ?? "Input submission is unavailable.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setLastRunId(null);

    try {
      if (!file) {
        setError("No file selected.");
        return;
      }

      const res = await submitFileInput(file);
      setResult(JSON.stringify(res, null, 2));

      if (res.run_id) {
        setLastRunId(res.run_id);
      }
    } catch (err: unknown) {
      setError(inputSubmissionApiErrorMessage(err));
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

      {accessMessage && (
        <p style={{ color: canSubmitInput ? undefined : "red" }}>
          {accessMessage}
        </p>
      )}

      <div>
        <h3>JSON Input</h3>
        <textarea
          rows={10}
          cols={60}
          value={jsonInput}
          onChange={(e) => setJsonInput(e.target.value)}
          disabled={controlsDisabled}
          title={
            canSubmitInput
              ? "Submit JSON input through the backend input boundary."
              : "JSON submission requires backend-derived input.submit permission."
          }
        />
        <br />
        <button
          onClick={handleJsonSubmit}
          disabled={controlsDisabled}
          title={
            canSubmitInput
              ? "Submit JSON input."
              : "JSON submission requires backend-derived input.submit permission."
          }
        >
          Submit JSON
        </button>
      </div>

      <hr />

      <div>
        <h3>File Upload</h3>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          disabled={controlsDisabled}
          title={
            canSubmitInput
              ? "Upload a file through the backend input boundary."
              : "File upload requires backend-derived input.submit permission."
          }
        />
        <br />
        <button
          onClick={handleFileSubmit}
          disabled={controlsDisabled || !file}
          title={
            canSubmitInput
              ? "Upload selected file."
              : "File upload requires backend-derived input.submit permission."
          }
        >
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