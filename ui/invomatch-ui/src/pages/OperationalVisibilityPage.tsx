import { useEffect, useState } from "react";
import {
  getOperationalAlerts,
  getOperationalHealthSummary,
  getOperationalMetrics,
} from "../services/api";
import type {
  ApiError,
  OperationalAlertsResponse,
  OperationalHealthSummaryResponse,
  OperationalMetricsResponse,
} from "../services/api";

type KeyValueTableProps = {
  title: string;
  values: Record<string, number | string>;
};

function KeyValueTable({ title, values }: KeyValueTableProps) {
  const entries = Object.entries(values);

  return (
    <div style={{ marginTop: 16 }}>
      <h3>{title}</h3>

      {entries.length === 0 ? (
        <p>No data available</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8 }}>
          <thead>
            <tr>
              <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                Key
              </th>
              <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                Value
              </th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([key, value]) => (
              <tr key={key}>
                <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{key}</td>
                <td style={{ borderBottom: "1px solid #333", padding: 8 }}>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function OperationalVisibilityPage() {
  const [metrics, setMetrics] = useState<OperationalMetricsResponse | null>(null);
  const [healthSummary, setHealthSummary] =
    useState<OperationalHealthSummaryResponse | null>(null);
  const [alerts, setAlerts] = useState<OperationalAlertsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadOperationalVisibility() {
      setLoading(true);
      setError(null);

      try {
        const [metricsResponse, healthSummaryResponse, alertsResponse] =
          await Promise.all([
            getOperationalMetrics(),
            getOperationalHealthSummary(),
            getOperationalAlerts(),
          ]);

        setMetrics(metricsResponse);
        setHealthSummary(healthSummaryResponse);
        setAlerts(alertsResponse);
      } catch (err: unknown) {
        const apiError = err as Partial<ApiError>;
        setError(apiError?.message ?? "Failed to load operational visibility data");
      } finally {
        setLoading(false);
      }
    }

    void loadOperationalVisibility();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Operational Visibility</h2>

      <p style={{ marginBottom: 16 }}>
        Admin-only operational dashboard. Access is enforced by the backend through
        operations.view_metrics.
      </p>

      {loading && <p>Loading operational visibility...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && metrics && healthSummary && alerts && (
        <>
          <div style={{ marginTop: 16 }}>
            <h3>Operational Status</h3>
            <p>Metrics Status: {metrics.status}</p>
            <p>Health Status: {healthSummary.status}</p>
            <p>Alert Status: {alerts.status}</p>
            <p>Metrics Generated At: {metrics.generated_at}</p>
            <p>Health Generated At: {healthSummary.generated_at}</p>
            <p>Alerts Generated At: {alerts.generated_at}</p>
            <p>Recommended Action: {healthSummary.recommended_action}</p>
          </div>

          <KeyValueTable title="Health Summary" values={healthSummary.summary} />
          <KeyValueTable title="Key Signals" values={healthSummary.signals} />
          <KeyValueTable title="Raw Counters" values={metrics.counters} />
          <KeyValueTable title="Decision Counts" values={metrics.decision_counts} />
          <KeyValueTable title="Reason Counts" values={metrics.reason_counts} />

          <div style={{ marginTop: 16 }}>
            <h3>Alerts</h3>

            {alerts.alerts.length === 0 ? (
              <p>No active alerts</p>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8 }}>
                <thead>
                  <tr>
                    <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                      Severity
                    </th>
                    <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                      Code
                    </th>
                    <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                      Message
                    </th>
                    <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                      Signal
                    </th>
                    <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                      Value
                    </th>
                    <th style={{ borderBottom: "1px solid #666", textAlign: "left", padding: 8 }}>
                      Recommended Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.alerts.map((alert) => (
                    <tr key={`${alert.code}-${alert.signal}`}>
                      <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
                        {alert.severity}
                      </td>
                      <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
                        {alert.code}
                      </td>
                      <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
                        {alert.message}
                      </td>
                      <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
                        {alert.signal}
                      </td>
                      <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
                        {alert.value}
                      </td>
                      <td style={{ borderBottom: "1px solid #333", padding: 8 }}>
                        {alert.recommended_action}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}