# InvoMatch Product Contract v1

## Purpose

This document defines the product-facing and API-facing contract for InvoMatch.

It describes what the system looks like from the outside:
- UI-facing objects
- API-facing objects
- user actions
- export shape

This document does not describe internal implementation.

---

## 1. Run Model (Product View)

The Run model represents a reconciliation job as visible to the user.

It is designed for:
- run list views
- run detail pages
- status badges
- progress bars
- summary cards
- export readiness

### Schema

```json
{
  "id": "run_01JX8Y7K9M3P4Q",
  "status": "review_required",
  "progress": {
    "percentage": 100,
    "stage_label": "Building review queue"
  },
  "summary": {
    "total_invoices": 128,
    "total_payments": 121,
    "matched": 89,
    "requires_review": 21,
    "unmatched": 12,
    "exceptions": 6
  },
  "timestamps": {
    "created_at": "2026-03-30T18:10:00Z",
    "updated_at": "2026-03-30T18:18:51Z",
    "completed_at": null
  },
  "error": null
}

