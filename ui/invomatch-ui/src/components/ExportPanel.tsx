import { useAuthSession } from "../auth/useAuthSession";
import type { RunArtifactReference, RunExportSummary } from "../services/api";

const ARTIFACTS_DOWNLOAD_PERMISSION = "artifacts.download";

type ExportPanelProps = {
  exportSummary: RunExportSummary;
  artifacts: RunArtifactReference[];
};

function downloadControlMessage(
  status: string,
  error: string | null,
  canDownloadArtifacts: boolean,
): string | null {
  if (status === "loading") {
    return "Artifact download controls are waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Artifact downloads are unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return error ?? "Artifact downloads are unavailable because the session could not be loaded.";
  }

  if (!canDownloadArtifacts) {
    return "Artifact downloads are hidden because the current session does not include artifacts.download.";
  }

  return null;
}

export default function ExportPanel({ exportSummary, artifacts }: ExportPanelProps) {
  const { status, error, hasPermission } = useAuthSession();

  const canDownloadArtifacts =
    status === "authenticated" &&
    hasPermission(ARTIFACTS_DOWNLOAD_PERMISSION);

  const controlMessage = downloadControlMessage(status, error, canDownloadArtifacts);

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Export Summary</h3>
      <p>Status: {exportSummary.status}</p>
      <p>Artifact Count: {exportSummary.artifact_count}</p>

      <h4>Artifacts</h4>
      {artifacts.length === 0 ? (
        <p>No artifacts available</p>
      ) : (
        <>
          <ul>
            {artifacts.map((artifact) => (
              <li key={artifact.artifact_id}>
                {artifact.file_name} ({artifact.media_type})
                {artifact.download_url && canDownloadArtifacts && (
                  <>
                    {" "}
                    <a href={artifact.download_url}>Download</a>
                  </>
                )}
              </li>
            ))}
          </ul>

          {artifacts.some((artifact) => artifact.download_url) && controlMessage && (
            <p style={{ color: "#555", marginTop: 8 }}>
              {controlMessage}
            </p>
          )}
        </>
      )}
    </div>
  );
}