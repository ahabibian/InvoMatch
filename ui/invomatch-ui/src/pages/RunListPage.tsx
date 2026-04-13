import { useEffect, useState } from "react";
import RunTable from "../components/RunTable";
import { listRuns } from "../services/api";
import type { ApiError, RunListItem } from "../services/api";

type RunListPageProps = {
  onSelectRun: (runId: string) => void;
};

export default function RunListPage({ onSelectRun }: RunListPageProps) {
  const [items, setItems] = useState<RunListItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRuns() {
      setLoading(true);
      setError(null);

      try {
        const response = await listRuns();
        setItems(response.items);
        setTotal(response.total);
      } catch (err: unknown) {
        const apiError = err as Partial<ApiError>;
        setError(apiError?.message ?? "Failed to load runs");
      } finally {
        setLoading(false);
      }
    }

    void loadRuns();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Run List</h2>

      {loading && <p>Loading runs...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && (
        <>
          <p>Total runs: {total}</p>
          <RunTable items={items} onSelectRun={onSelectRun} />
        </>
      )}
    </div>
  );
}