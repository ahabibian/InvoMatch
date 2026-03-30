# InvoMatch Product Contract v1

## 1. Run Model (Product View)

### Schema

{
  "id": "run_x",
  "status": "processing",
  "progress": {
    "percentage": 50,
    "stage_label": "Matching records"
  },
  "summary": {
    "total_invoices": 0,
    "total_payments": 0,
    "matched": 0,
    "requires_review": 0,
    "unmatched": 0,
    "exceptions": 0
  },
  "timestamps": {
    "created_at": "",
    "updated_at": "",
    "completed_at": null
  },
  "error": null
}

### Status

queued | processing | review_required | completed | failed | cancelled
