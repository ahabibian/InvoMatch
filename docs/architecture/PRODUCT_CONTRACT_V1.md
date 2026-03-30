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

