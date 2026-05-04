import { useCallback, useEffect, useState } from "react";
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
  emptyMessage: string;
  title: string;
  values: Record<string, number | string>;
};

type OperationalVisibilityState = {
  alerts: OperationalAlertsResponse | null;
  healthSummary: OperationalHealthSummaryResponse | null;
  metrics: OperationalMetricsResponse | null;
};

const initialOperationalVisibilityState: OperationalVisibilityState = {
  alerts: null,
  healthSummary: null,
  metrics: null,
};

function formatClientTimestamp(value: Date | null): string {
  if (!value) {
    return "Not loaded yet";
  }

  return value.toLocaleString();
}

function getOperationalErrorMessage(err: unknown): string {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401 || apiError?.status === 403) {
    return [
      "Operational visibility is restricted by backend authorization.",
      "The current request was not authorized for operations.view_metrics.",
      "Frontend role-aware navigation is not available yet because the UI has no session, role, or permission context.",
    ].join(" ");
  }

  return apiError?.message ?? "Failed to load operational visibility data.";
}

function KeyValueTable({ emptyMessage, title, values }: KeyValueTableProps) {
  const entries = Object.entries(values);

  return (
    <div style={{ marginTop: 16 }}>
      <h3>{title}</h3>

      {entries.length === 0 ? (
        <p>{emptyMessage}</p>
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
  const [data, setData] = useState<OperationalVisibilityState>(
    initialOperationalVisibilityState,
  );
  const [lastLoadedAt, setLastLoadedAt] = useState<Date | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOperationalVisibility = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [metricsResponse, healthSummaryResponse, alertsResponse] =
        await Promise.all([
          getOperationalMetrics(),
          getOperationalHealthSummary(),
          getOperationalAlerts(),
        ]);

      setData({
        alerts: alertsResponse,
        healthSummary: healthSummaryResponse,
        metrics: metricsResponse,
      });
      setLastLoadedAt(new Date());
    } catch (err: unknown) {
      setError(getOperationalErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOperationalVisibility();
  }, [loadOperationalVisibility]);

  const { alerts, healthSummary, metrics } = data;
  const hasCompleteData = Boolean(metrics && healthSummary && alerts);

  return (
    <div style={{ padding: 20 }}>
      <h2>Operational Visibility</h2>

      <p style={{ marginBottom: 12 }}>
        Admin-only operational dashboard. Access is enforced by the backend through
        operations.view_metrics.
      </p>

      <p style={{ marginBottom: 16 }}>
        Frontend role-aware navigation is not enabled yet because the current UI has
        no authenticated user, role, or permission context. The backend remains the
        security boundary.
      </p>

      <div style={{ marginBottom: 16 }}>
        <button
          disabled={loading}
          onClick={() => {
            void loadOperationalVisibility();
          }}
          style={{ marginRight: 12 }}
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
        <span>Last loaded: {formatClientTimestamp(lastLoadedAt)}</span>
      </div>

      {loading && !hasCompleteData && (
        <p>Loading operational visibility from the backend...</p>
      )}

      {error && (
        <div
          role="alert"
          style={{
            border: "1px solid #a33",
            color: "red",
            marginBottom: 16,
            padding: 12,
          }}
        >
          <strong>Operational visibility unavailable.</strong>
          <p style={{ marginBottom: 0 }}>{error}</p>
        </div>
      )}

      {!loading && !error && !hasCompleteData && (
        <p>
          No operational visibility payload is available. Refresh the dashboard or
          inspect backend availability and authorization.
        </p>
      )}

      {hasCompleteData && metrics && healthSummary && alerts && (
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

          <KeyValueTable
            emptyMessage="No health summary fields were returned by the backend."
            title="Health Summary"
            values={healthSummary.summary}
          />
          <KeyValueTable
            emptyMessage="No operational health signals were returned by the backend."
            title="Key Signals"
            values={healthSummary.signals}
          />
          <KeyValueTable
            emptyMessage="No raw operational counters were returned by the backend."
            title="Raw Counters"
            values={metrics.counters}
          />
          <KeyValueTable
            emptyMessage="No operational decision counts were returned by the backend."
            title="Decision Counts"
            values={metrics.decision_counts}
          />
          <KeyValueTable
            emptyMessage="No operational reason counts were returned by the backend."
            title="Reason Counts"
            values={metrics.reason_counts}
          />

          <div style={{ marginTop: 16 }}>
            <h3>Alerts</h3>

            {alerts.alerts.length === 0 ? (
              <p>No active operational alerts were returned by the backend.</p>
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