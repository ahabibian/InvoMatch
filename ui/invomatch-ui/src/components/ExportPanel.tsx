import type { RunArtifactReference, RunExportSummary } from "../services/api";

type ExportPanelProps = {
  exportSummary: RunExportSummary;
  artifacts: RunArtifactReference[];
};

export default function ExportPanel({ exportSummary, artifacts }: ExportPanelProps) {
  return (
    <div style={{ marginTop: 16 }}>
      <h3>Export Summary</h3>
      <p>Status: {exportSummary.status}</p>
      <p>Artifact Count: {exportSummary.artifact_count}</p>

      <h4>Artifacts</h4>
      {artifacts.length === 0 ? (
        <p>No artifacts available</p>
      ) : (
        <ul>
          {artifacts.map((artifact) => (
            <li key={artifact.artifact_id}>
              {artifact.file_name} ({artifact.media_type})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}