
import { useEffect, useState } from "react";
import { useAuthSession } from "../auth/useAuthSession";
import { getReviewMatchDetail } from "../services/api";
import type { ApiError, MatchDetailResponse } from "../services/api";

const RUNS_READ_REVIEW_PERMISSION = "runs.read_review";

type MatchDetailPanelProps = {
matchId: string;
};

type MatchDetailLoadState =
| "loading"
| "loaded"
| "unavailable"
| "not_found"
| "malformed"
| "backend_failure";

type BackendRecord = Record<string, unknown>;

function isBackendObject(value: unknown): value is BackendRecord {
return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function asBackendRecord(value: unknown): BackendRecord | null {
return isBackendObject(value) ? value : null;
}

function asBackendRecordArray(value: unknown): BackendRecord[] {
if (!Array.isArray(value)) {
return [];
}

return value.filter(isBackendObject);
}

function asDisplayValue(value: unknown): string {
if (value === null || value === undefined) {
return "—";
}

if (typeof value === "string") {
return value.trim().length > 0 ? value : "—";
}

if (typeof value === "number" || typeof value === "boolean") {
return String(value);
}

return JSON.stringify(value);
}

function getBackendText(source: BackendRecord | null, key: string): string | null {
if (!source) {
return null;
}

const value = source[key];

if (typeof value !== "string") {
return null;
}

const trimmed = value.trim();
return trimmed.length > 0 ? trimmed : null;
}

function getBackendFailureDetail(err: unknown): BackendRecord | null {
const apiError = err as Partial<ApiError>;
return asBackendRecord(apiError?.details);
}

function classifyMatchDetailApiError(err: unknown): {
state: MatchDetailLoadState;
message: string;
backendFailure: BackendRecord | null;
} {
const apiError = err as Partial<ApiError>;
const backendFailure = getBackendFailureDetail(err);
const backendMessage = getBackendText(backendFailure, "message");

if (apiError?.status === 401) {
return {
state: "unavailable",
message:
backendMessage ??
"Match Detail access was denied because the backend did not authenticate the current request.",
backendFailure,
};
}

if (apiError?.status === 403) {
return {
state: "unavailable",
message:
backendMessage ??
"Match Detail access was denied by backend authorization for runs.read_review.",
backendFailure,
};
}

if (apiError?.status === 404) {
return {
state: "not_found",
message:
backendMessage ??
"Match Detail was not found for the selected backend-owned match_id.",
backendFailure,
};
}

if (apiError?.status === 422) {
return {
state: "malformed",
message:
backendMessage ??
"Match Detail response was rejected by backend-owned malformed payload semantics.",
backendFailure,
};
}

return {
state: "backend_failure",
message: backendMessage ?? apiError?.message ?? "Failed to load Match Detail from the backend-owned route.",
backendFailure,
};
}

function SummaryBlock({
title,
value,
}: {
title: string;
value: unknown;
}) {
const record = asBackendRecord(value);
const entries = record ? Object.entries(record) : [];

return (
<section style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
<h3 style={{ marginTop: 0 }}>{title}</h3>
{entries.length === 0 ? (
<p style={{ color: "#555", marginBottom: 0 }}>No backend-owned summary values were provided.</p>
) : (
<dl style={{ display: "grid", gap: 8, gridTemplateColumns: "180px 1fr", margin: 0 }}>
{entries.map(([key, entryValue]) => (
<div key={key} style={{ display: "contents" }}>
<dt style={{ fontWeight: 700 }}>{key}</dt>
<dd style={{ margin: 0 }}>{asDisplayValue(entryValue)}</dd>
</div>
))}
</dl>
)}
</section>
);
}

function EvidenceBlock({ evidence }: { evidence: unknown }) {
const items = asBackendRecordArray(evidence);

return (
<section style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
<h3 style={{ marginTop: 0 }}>Backend-owned evidence</h3>
{items.length === 0 ? (
<p style={{ color: "#555", marginBottom: 0 }}>No backend-owned evidence items were provided.</p>
) : (
<table style={{ borderCollapse: "collapse", width: "100%" }}>
<thead>
<tr>
<th style={{ borderBottom: "1px solid #ddd", padding: 8, textAlign: "left" }}>Evidence ID</th>
<th style={{ borderBottom: "1px solid #ddd", padding: 8, textAlign: "left" }}>Type</th>
<th style={{ borderBottom: "1px solid #ddd", padding: 8, textAlign: "left" }}>Label</th>
<th style={{ borderBottom: "1px solid #ddd", padding: 8, textAlign: "left" }}>Value</th>
<th style={{ borderBottom: "1px solid #ddd", padding: 8, textAlign: "left" }}>Source</th>
</tr>
</thead>
<tbody>
{items.map((item, index) => (
<tr key={String(item.evidence_id ?? "evidence") + "-" + String(index)}>
<td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{asDisplayValue(item.evidence_id)}</td>
<td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{asDisplayValue(item.evidence_type)}</td>
<td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{asDisplayValue(item.label)}</td>
<td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{asDisplayValue(item.value)}</td>
<td style={{ borderBottom: "1px solid #eee", padding: 8 }}>{asDisplayValue(item.source)}</td>
</tr>
))}
</tbody>
</table>
)}
</section>
);
}

function TraceabilityBlock({ traceability }: { traceability: unknown }) {
const record = asBackendRecord(traceability);

return (
<section style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
<h3 style={{ marginTop: 0 }}>Backend-owned traceability</h3>
{!record ? (
<p style={{ color: "#555", marginBottom: 0 }}>No backend-owned traceability payload was provided.</p>
) : (
<dl style={{ display: "grid", gap: 8, gridTemplateColumns: "180px 1fr", margin: 0 }}>
{Object.entries(record).map(([key, value]) => (
<div key={key} style={{ display: "contents" }}>
<dt style={{ fontWeight: 700 }}>{key}</dt>
<dd style={{ margin: 0 }}>{asDisplayValue(value)}</dd>
</div>
))}
</dl>
)}
</section>
);
}

function ExplanationBlock({ explanation }: { explanation: unknown }) {
const entries = Array.isArray(explanation) ? explanation : [];

return (
<section style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
<h3 style={{ marginTop: 0 }}>Backend-owned explanation</h3>
{entries.length === 0 ? (
<p style={{ color: "#555", marginBottom: 0 }}>No backend-owned explanation entries were provided.</p>
) : (
<ul style={{ marginBottom: 0 }}>
{entries.map((entry, index) => (
<li key={index}>{asDisplayValue(entry)}</li>
))}
</ul>
)}
</section>
);
}

function FailureBlock({ failure }: { failure: unknown }) {
const record = asBackendRecord(failure);

return (
<section style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
<h3 style={{ marginTop: 0 }}>Backend-owned failure semantics</h3>
{!record ? (
<p style={{ color: "#555", marginBottom: 0 }}>No backend-owned failure payload was provided.</p>
) : (
<dl style={{ display: "grid", gap: 8, gridTemplateColumns: "180px 1fr", margin: 0 }}>
<div style={{ display: "contents" }}>
<dt style={{ fontWeight: 700 }}>code</dt>
<dd style={{ margin: 0 }}>{asDisplayValue(record.code)}</dd>
</div>
<div style={{ display: "contents" }}>
<dt style={{ fontWeight: 700 }}>message</dt>
<dd style={{ margin: 0 }}>{asDisplayValue(record.message)}</dd>
</div>
</dl>
)}
</section>
);
}

function BackendFailureAlert({
loadState,
message,
backendFailure,
}: {
loadState: MatchDetailLoadState;
message: string | null;
backendFailure: BackendRecord | null;
}) {
return (
<div
role="alert"
style={{ border: "1px solid #a33", color: "red", marginBottom: 16, padding: 12 }}
>
<strong>
{loadState === "unavailable" && "Match Detail unavailable."}
{loadState === "not_found" && "Match Detail not found."}
{loadState === "malformed" && "Match Detail malformed."}
{loadState === "backend_failure" && "Match Detail backend failure."}
</strong>
<p>{message}</p>
{backendFailure && (
<dl style={{ display: "grid", gap: 8, gridTemplateColumns: "180px 1fr", marginBottom: 0 }}>
<div style={{ display: "contents" }}>
<dt style={{ fontWeight: 700 }}>Backend failure code</dt>
<dd style={{ margin: 0 }}>{asDisplayValue(backendFailure.code)}</dd>
</div>
<div style={{ display: "contents" }}>
<dt style={{ fontWeight: 700 }}>Backend failure message</dt>
<dd style={{ margin: 0 }}>{asDisplayValue(backendFailure.message)}</dd>
</div>
</dl>
)}
</div>
);
}

export default function MatchDetailPanel({ matchId }: MatchDetailPanelProps) {
const {
status: sessionStatus,
error: sessionError,
hasPermission,
} = useAuthSession();

const [loadState, setLoadState] = useState<MatchDetailLoadState>("loading");
const [message, setMessage] = useState<string | null>(null);
const [backendFailure, setBackendFailure] = useState<BackendRecord | null>(null);
const [detail, setDetail] = useState<MatchDetailResponse | null>(null);

const canReadReview =
sessionStatus === "authenticated" &&
hasPermission(RUNS_READ_REVIEW_PERMISSION);

useEffect(() => {
let cancelled = false;

async function loadMatchDetail() {
  if (sessionStatus === "loading") {
    setDetail(null);
    setBackendFailure(null);
    setLoadState("loading");
    setMessage(null);
    return;
  }

  if (sessionStatus === "unauthenticated") {
    setDetail(null);
    setBackendFailure(null);
    setLoadState("unavailable");
    setMessage("Match Detail is unavailable because the current session is not authenticated.");
    return;
  }

  if (sessionStatus === "error") {
    setDetail(null);
    setBackendFailure(null);
    setLoadState("unavailable");
    setMessage(sessionError ?? "Match Detail is unavailable because the session could not be loaded.");
    return;
  }

  if (!canReadReview) {
    setDetail(null);
    setBackendFailure(null);
    setLoadState("unavailable");
    setMessage("Match Detail is hidden because the current session does not include runs.read_review.");
    return;
  }

  if (!matchId || matchId.trim().length === 0) {
    setDetail(null);
    setBackendFailure(null);
    setLoadState("unavailable");
    setMessage("Match Detail cannot load because no match_id was selected by the App shell.");
    return;
  }

  setDetail(null);
  setBackendFailure(null);
  setLoadState("loading");
  setMessage(null);

  try {
    const response = await getReviewMatchDetail(matchId);

    if (cancelled) {
      return;
    }

    if (!isBackendObject(response)) {
      setDetail(null);
      setBackendFailure({
        code: "malformed_frontend_observation",
        message: "Backend response was not an object payload.",
      });
      setLoadState("malformed");
      setMessage("Match Detail response was malformed because the backend did not return an object payload.");
      return;
    }

    const responseMatchId = response.match_id;

    if (
      typeof responseMatchId === "string" &&
      responseMatchId.trim().length > 0 &&
      responseMatchId !== matchId
    ) {
      setDetail(null);
      setBackendFailure({
        code: "match_id_mismatch",
        message: "Returned backend match_id did not match the selected App shell match_id.",
      });
      setLoadState("malformed");
      setMessage("Match Detail response was malformed because the returned match_id did not match the selected match_id.");
      return;
    }

    setDetail(response);
    setBackendFailure(asBackendRecord(response.failure));
    setLoadState("loaded");
    setMessage(null);
  } catch (err: unknown) {
    if (cancelled) {
      return;
    }

    const classified = classifyMatchDetailApiError(err);
    setDetail(null);
    setBackendFailure(classified.backendFailure);
    setLoadState(classified.state);
    setMessage(classified.message);
  }
}

void loadMatchDetail();

return () => {
  cancelled = true;
};

}, [canReadReview, matchId, sessionError, sessionStatus]);

return (
<section
aria-label="Match Detail"
style={{ border: "1px solid #aaa", margin: "0 20px 20px", padding: 16 }}
>
<h2>Match Detail</h2>

  <p style={{ color: "#555", maxWidth: 760 }}>
    This controlled loading boundary uses only the App shell selected match_id and fetches
    backend-owned Match Detail data from GET /api/review/matches/:match_id/detail. It renders
    only backend-provided evidence, traceability, confidence, explanation, and failure fields.
  </p>

  <p>
    Selected match_id: <code>{matchId}</code>
  </p>

  {loadState === "loading" && (
    <p role="status">Loading Match Detail from backend-owned route...</p>
  )}

  {loadState !== "loading" && loadState !== "loaded" && (
    <BackendFailureAlert
      loadState={loadState}
      message={message}
      backendFailure={backendFailure}
    />
  )}

  {loadState === "loaded" && detail && (
    <div>
      <section style={{ border: "1px solid #ddd", marginBottom: 12, padding: 12 }}>
        <h3 style={{ marginTop: 0 }}>Backend-owned trust summary</h3>
        <dl style={{ display: "grid", gap: 8, gridTemplateColumns: "180px 1fr", margin: 0 }}>
          <div style={{ display: "contents" }}>
            <dt style={{ fontWeight: 700 }}>match_id</dt>
            <dd style={{ margin: 0 }}>{asDisplayValue(detail.match_id)}</dd>
          </div>
          <div style={{ display: "contents" }}>
            <dt style={{ fontWeight: 700 }}>match_status</dt>
            <dd style={{ margin: 0 }}>{asDisplayValue(detail.match_status)}</dd>
          </div>
          <div style={{ display: "contents" }}>
            <dt style={{ fontWeight: 700 }}>confidence</dt>
            <dd style={{ margin: 0 }}>{asDisplayValue(detail.confidence)}</dd>
          </div>
        </dl>
      </section>

      <SummaryBlock title="Backend-owned invoice summary" value={detail.invoice_summary} />
      <SummaryBlock title="Backend-owned payment summary" value={detail.payment_summary} />
      <EvidenceBlock evidence={detail.evidence} />
      <TraceabilityBlock traceability={detail.traceability} />
      <ExplanationBlock explanation={detail.explanation} />
      <FailureBlock failure={detail.failure} />

      <details>
        <summary>Raw backend-owned Match Detail response</summary>
        <pre
          aria-label="Backend-owned Match Detail response"
          style={{
            background: "#f7f7f7",
            border: "1px solid #ddd",
            overflowX: "auto",
            padding: 12,
            whiteSpace: "pre-wrap",
          }}
        >
          {JSON.stringify(detail, null, 2)}
        </pre>
      </details>
    </div>
  )}
</section>

);
}
