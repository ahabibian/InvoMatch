import { useAuthSession } from "../auth/useAuthSession";
import type { RunReviewSummary } from "../services/api";

const RUNS_READ_REVIEW_PERMISSION = "runs.read_review";

type ReviewPanelProps = {
  reviewSummary: RunReviewSummary;
};

function reviewSurfaceMessage(
  status: string,
  error: string | null,
  canReadReview: boolean,
): string | null {
  if (status === "loading") {
    return "Review summary is waiting for the authenticated session.";
  }

  if (status === "unauthenticated") {
    return "Review summary is unavailable because the current session is not authenticated.";
  }

  if (status === "error") {
    return error ?? "Review summary is unavailable because the session could not be loaded.";
  }

  if (!canReadReview) {
    return "Review summary is hidden because the current session does not include runs.read_review.";
  }

  return null;
}

export default function ReviewPanel({ reviewSummary }: ReviewPanelProps) {
  const { status, error, hasPermission } = useAuthSession();

  const canReadReview =
    status === "authenticated" &&
    hasPermission(RUNS_READ_REVIEW_PERMISSION);

  const surfaceMessage = reviewSurfaceMessage(status, error, canReadReview);

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Review Summary</h3>

      {surfaceMessage ? (
        <p style={{ color: "#555" }}>{surfaceMessage}</p>
      ) : (
        <>
          <p>Status: {reviewSummary.status}</p>
          <p>Total Items: {reviewSummary.total_items}</p>
          <p>Open Items: {reviewSummary.open_items}</p>
          <p>Resolved Items: {reviewSummary.resolved_items}</p>
        </>
      )}
    </div>
  );
}
