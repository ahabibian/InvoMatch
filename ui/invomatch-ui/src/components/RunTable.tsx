import type { RunListItem } from "../services/api";

type RunTableProps = {
  items: RunListItem[];
  onSelectRun: (runId: string) => void;
};

export default function RunTable({ items, onSelectRun }: RunTableProps) {
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 16 }}>
      <thead>
        <tr>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Run ID</th>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Status</th>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Created</th>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Updated</th>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Matches</th>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Review Required</th>
          <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>Action</th>
        </tr>
      </thead>
      <tbody>
        {items.map((run) => (
          <tr key={run.run_id}>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{run.run_id}</td>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{run.status}</td>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{run.created_at ?? "-"}</td>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{run.updated_at ?? "-"}</td>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{run.match_count ?? 0}</td>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{run.review_required_count ?? 0}</td>
            <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
              <button onClick={() => onSelectRun(run.run_id)}>
                Open
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}