import type { RunReviewSummary } from "../services/api";

type ReviewPanelProps = {
  reviewSummary: RunReviewSummary;
};

export default function ReviewPanel({ reviewSummary }: ReviewPanelProps) {
  return (
    <div style={{ marginTop: 16 }}>
      <h3>Review Summary</h3>
      <p>Status: {reviewSummary.status}</p>
      <p>Total Items: {reviewSummary.total_items}</p>
      <p>Open Items: {reviewSummary.open_items}</p>
      <p>Resolved Items: {reviewSummary.resolved_items}</p>
    </div>
  );
}