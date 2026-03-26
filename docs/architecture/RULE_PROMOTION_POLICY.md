# RULE PROMOTION POLICY

## Purpose
Define how candidate learned behavior becomes production-safe rule behavior.

## Promotion stages
1. signal extracted
2. candidate rule drafted
3. validation checks
4. replay/shadow evaluation
5. approval
6. activation
7. monitoring
8. rollback if needed

## Promotion requirements
- minimum evidence threshold
- minimum consistency score
- reviewer disagreement below threshold
- tenant scope explicitly defined
- replay test passed
- rollback path exists
- rule version assigned
- approver recorded

## Rollback requirements
- any promoted rule must be deactivatable
- rollback must preserve audit history
- superseded rules must remain queryable
- impacted runs must remain explainable by version

## Anti-patterns
- auto-promote from raw feedback
- modify active rules without version bump
- overwrite historical rule state
- cross-tenant leakage