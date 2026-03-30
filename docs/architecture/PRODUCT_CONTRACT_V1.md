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

