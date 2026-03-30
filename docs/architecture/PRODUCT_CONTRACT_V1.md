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

---

## 2. Match Result (User-facing)

The Match Result model represents a suggested or final match in a user-facing format.

### Schema

{
  "match_id": "match_01JX9A2BC3D4E",
  "state": "suggested",
  "invoice": {
    "id": "inv_10023",
    "invoice_number": "INV-2026-00123",
    "date": "2026-03-01",
    "amount": 1250.00,
    "currency": "SEK",
    "vendor_name": "Nordic Office AB"
  },
  "payment": {
    "id": "pay_88421",
    "payment_reference": "PAY-2026-88421",
    "date": "2026-03-05",
    "amount": 1250.00,
    "currency": "SEK",
    "payer_name": "Nordic Office AB"
  },
  "suggested_match": true,
  "confidence": "high",
  "reason": "Amount, currency, and vendor name are aligned.",
  "requires_review": false
}

### State Values

suggested | accepted | rejected | manual | exception

### Confidence Values

low | medium | high


---

## 3. Review Case

The Review Case represents situations that require user decision.

### Schema

{
  "case_id": "case_01JX9C88A1B2C",
  "type": "ambiguity",
  "invoice": {
    "id": "inv_10023",
    "invoice_number": "INV-2026-00123",
    "amount": 1250.00,
    "currency": "SEK"
  },
  "candidates": [
    {
      "payment_id": "pay_88421",
      "amount": 1250.00,
      "date": "2026-03-05",
      "confidence": "medium"
    }
  ],
  "recommended_action": "select_best_match",
  "explanation": "Multiple payments match the same invoice amount."
}

### Types

ambiguity | conflict | unmatched

### Actions

select_best_match | review_manually | mark_as_exception


---

## 4. User Action Model

The User Action Model defines the actions a user can submit from the product UI.

### Action Envelope

{
  "action": "accept_match",
  "run_id": "run_01JX8Y7K9M3P4Q",
  "payload": {}
}

### accept_match

Required inputs:
- match_id

Expected effect:
- the selected match becomes accepted
- the item leaves the review queue
- run summary is updated

{
  "action": "accept_match",
  "run_id": "run_01JX8Y7K9M3P4Q",
  "payload": {
    "match_id": "match_01JX9A2BC3D4E"
  }
}

### reject_match

Required inputs:
- match_id

Optional inputs:
- reason

Expected effect:
- the selected match is rejected
- the item is removed from accepted results
- run summary is updated

{
  "action": "reject_match",
  "run_id": "run_01JX8Y7K9M3P4Q",
  "payload": {
    "match_id": "match_01JX9A2BC3D4E",
    "reason": "Wrong payment selected"
  }
}

### manual_link

Required inputs:
- invoice_id
- payment_id

Optional inputs:
- note

Expected effect:
- a manual match is created
- the item leaves the review queue
- the result state becomes manual

{
  "action": "manual_link",
  "run_id": "run_01JX8Y7K9M3P4Q",
  "payload": {
    "invoice_id": "inv_10023",
    "payment_id": "pay_88421",
    "note": "Confirmed manually by reviewer"
  }
}

### mark_exception

Required inputs:
- invoice_id

Optional inputs:
- reason

Expected effect:
- the item is marked as an exception
- the item leaves review or unmatched queues
- run summary is updated

{
  "action": "mark_exception",
  "run_id": "run_01JX8Y7K9M3P4Q",
  "payload": {
    "invoice_id": "inv_10023",
    "reason": "Invoice should be excluded from reconciliation"
  }
}

### Supported Actions

accept_match | reject_match | manual_link | mark_exception


---

## 5. Export Model

The Export Model represents the final output of a reconciliation run.

### Schema

{
  "run_id": "run_01JX8Y7K9M3P4Q",
  "generated_at": "2026-03-30T19:00:00Z",
  "final_matches": [],
  "unmatched": [],
  "exceptions": [],
  "audit": {}
}

### final_matches

[
  {
    "match_id": "match_01",
    "invoice_id": "inv_10023",
    "payment_id": "pay_88421",
    "amount": 1250.00,
    "currency": "SEK",
    "status": "accepted"
  }
]

### unmatched

[
  {
    "invoice_id": "inv_10050",
    "amount": 900.00,
    "currency": "SEK"
  }
]

### exceptions

[
  {
    "invoice_id": "inv_10077",
    "reason": "Marked as exception by user"
  }
]

### audit

{
  "total_invoices": 128,
  "matched": 89,
  "unmatched": 12,
  "exceptions": 6,
  "reviewed": 21
}


---

## 6. API Surface (v1)

The API Surface defines the user-facing API for the InvoMatch product.

### GET /runs

Request shape:

{
  "query": {
    "status": "optional",
    "limit": "optional",
    "cursor": "optional"
  }
}

Response shape:

{
  "items": [
    {
      "id": "run_01JX8Y7K9M3P4Q",
      "status": "processing",
      "progress": {
        "percentage": 50,
        "stage_label": "Matching records"
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
        "updated_at": "2026-03-30T18:14:32Z",
        "completed_at": null
      },
      "error": null
    }
  ],
  "next_cursor": null
}

### GET /runs/{id}

Request shape:

{
  "path": {
    "id": "run id"
  }
}

Response shape:

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

### GET /runs/{id}/review

Request shape:

{
  "path": {
    "id": "run id"
  }
}

Response shape:

{
  "run_id": "run_01JX8Y7K9M3P4Q",
  "items": [
    {
      "case_id": "case_01JX9C88A1B2C",
      "type": "ambiguity",
      "invoice": {
        "id": "inv_10023",
        "invoice_number": "INV-2026-00123",
        "amount": 1250.00,
        "currency": "SEK"
      },
      "candidates": [
        {
          "payment_id": "pay_88421",
          "amount": 1250.00,
          "date": "2026-03-05",
          "confidence": "medium"
        }
      ],
      "recommended_action": "select_best_match",
      "explanation": "Multiple payments match the same invoice amount."
    }
  ]
}

### POST /runs/{id}/actions

Request shape:

{
  "action": "accept_match",
  "payload": {
    "match_id": "match_01JX9A2BC3D4E"
  }
}

Response shape:

{
  "run_id": "run_01JX8Y7K9M3P4Q",
  "action": "accept_match",
  "result": "accepted",
  "message": "The action was applied successfully.",
  "updated_summary": {
    "total_invoices": 128,
    "total_payments": 121,
    "matched": 90,
    "requires_review": 20,
    "unmatched": 12,
    "exceptions": 6
  }
}

### GET /runs/{id}/export

Request shape:

{
  "path": {
    "id": "run id"
  }
}

Response shape:

{
  "run_id": "run_01JX8Y7K9M3P4Q",
  "generated_at": "2026-03-30T19:00:00Z",
  "final_matches": [
    {
      "match_id": "match_01",
      "invoice_id": "inv_10023",
      "payment_id": "pay_88421",
      "amount": 1250.00,
      "currency": "SEK",
      "status": "accepted"
    }
  ],
  "unmatched": [
    {
      "invoice_id": "inv_10050",
      "amount": 900.00,
      "currency": "SEK"
    }
  ],
  "exceptions": [
    {
      "invoice_id": "inv_10077",
      "reason": "Marked as exception by user"
    }
  ],
  "audit": {
    "total_invoices": 128,
    "matched": 89,
    "unmatched": 12,
    "exceptions": 6,
    "reviewed": 21
  }
}

