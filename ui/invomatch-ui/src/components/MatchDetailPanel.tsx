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

function isBackendObject(value: unknown): value is MatchDetailResponse {
return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function classifyMatchDetailApiError(err: unknown): {
state: MatchDetailLoadState;
message: string;
} {
const apiError = err as Partial<ApiError>;

if (apiError?.status === 401) {
return {
state: "unavailable",
message: "Match Detail access was denied because the backend did not authenticate the current request.",
};
}

if (apiError?.status === 403) {
return {
state: "unavailable",
message: "Match Detail access was denied by backend authorization for runs.read_review.",
};
}

if (apiError?.status === 404) {
return {
state: "not_found",
message: "Match Detail was not found for the selected backend-owned match_id.",
};
}

return {
state: "backend_failure",
message: apiError?.message ?? "Failed to load Match Detail from the backend-owned route.",
};
}

export default function MatchDetailPanel({ matchId }: MatchDetailPanelProps) {
const {
status: sessionStatus,
error: sessionError,
hasPermission,
} = useAuthSession();

const [loadState, setLoadState] = useState<MatchDetailLoadState>("loading");
const [message, setMessage] = useState<string | null>(null);
const [detail, setDetail] = useState<MatchDetailResponse | null>(null);

const canReadReview =
sessionStatus === "authenticated" &&
hasPermission(RUNS_READ_REVIEW_PERMISSION);

useEffect(() => {
let cancelled = false;

async function loadMatchDetail() {
  if (sessionStatus === "loading") {
    setDetail(null);
    setLoadState("loading");
    setMessage(null);
    return;
  }

  if (sessionStatus === "unauthenticated") {
    setDetail(null);
    setLoadState("unavailable");
    setMessage("Match Detail is unavailable because the current session is not authenticated.");
    return;
  }

  if (sessionStatus === "error") {
    setDetail(null);
    setLoadState("unavailable");
    setMessage(sessionError ?? "Match Detail is unavailable because the session could not be loaded.");
    return;
  }

  if (!canReadReview) {
    setDetail(null);
    setLoadState("unavailable");
    setMessage("Match Detail is hidden because the current session does not include runs.read_review.");
    return;
  }

  if (!matchId || matchId.trim().length === 0) {
    setDetail(null);
    setLoadState("unavailable");
    setMessage("Match Detail cannot load because no match_id was selected by the App shell.");
    return;
  }

  setDetail(null);
  setLoadState("loading");
  setMessage(null);

  try {
    const response = await getReviewMatchDetail(matchId);

    if (cancelled) {
      return;
    }

    if (!isBackendObject(response)) {
      setDetail(null);
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
      setLoadState("malformed");
      setMessage("Match Detail response was malformed because the returned match_id did not match the selected match_id.");
      return;
    }

    setDetail(response);
    setLoadState("loaded");
    setMessage(null);
  } catch (err: unknown) {
    if (cancelled) {
      return;
    }

    const classified = classifyMatchDetailApiError(err);
    setDetail(null);
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
    backend-owned Match Detail data from GET /api/review/matches/:match_id/detail. It does
    not synthesize frontend evidence, trust, error, or Review Queue row payload data.
  </p>

  <p>
    Selected match_id: <code>{matchId}</code>
  </p>

  {loadState === "loading" && (
    <p role="status">Loading Match Detail from backend-owned route...</p>
  )}

  {loadState !== "loading" && loadState !== "loaded" && (
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
      <p style={{ marginBottom: 0 }}>{message}</p>
    </div>
  )}

  {loadState === "loaded" && detail && (
    <div>
      <p style={{ color: "#555" }}>
        Backend-owned Match Detail response loaded. Scenario 15 remains incomplete until
        evidence, trust, and error rendering are validated end-to-end.
      </p>

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
    </div>
  )}
</section>

);
}
