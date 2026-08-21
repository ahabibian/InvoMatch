Mini-EPIC 32.148 — Canonical Release Authorization Blocker Remediation Boundary

Purpose

Mini-EPIC 32.148 follows the genuine blocked action-specific authorization recorded by Mini-EPIC 32.147. It remediates the release-subject evidence that can be established without external mutation, defines a bounded actor/process and failure contract, and evaluates whether sufficient evidence now exists for fresh authorization re-evaluation.

This boundary does not re-authorize GitHub Release creation, establish execution readiness, implement Mini-EPIC 32.149 or 32.150, or perform an operational release action.

Immediate Authoritative Predecessor

Mini-EPIC 32.147 is the immediate authoritative predecessor.

Mini-EPIC 32.147 was merged through PR #40 at commit `34f7171cbf05495473b4f539fe818533cbd4b62f` and records:

CANONICAL_RELEASE_EXECUTION_OR_PUBLICATION_GOVERNANCE_AUTHORIZATION_BLOCKED

The authoritative incoming state remains:

CANONICAL_RELEASE_READINESS_VALIDATION_STABILIZED

CANONICAL_RELEASE_READINESS_APPROVED

CANONICAL_RELEASE_EXECUTION_OR_PUBLICATION_GOVERNANCE_BOUNDARY_DEFINED

READY_FOR_CANONICAL_RELEASE_EXECUTION_OR_PUBLICATION_GOVERNANCE_AUTHORIZATION_BOUNDARY

CANONICAL_RELEASE_EXECUTION_OR_PUBLICATION_GOVERNANCE_AUTHORIZATION_BLOCKED

Original Blocker Matrix

Mini-EPIC 32.147 identified four blockers for the exact action GitHub Release creation on the GitHub Releases surface of `ahabibian/InvoMatch`:

1. Complete release-subject identity was missing: no matching package/archive, manifest, digest, build/release-candidate identity, or coherent operational release version was bound to the approved source.
2. Actor/process authority was missing: no canonical authorized operator or repository-controlled release process was identified.
3. Operational capability evidence was missing: active automation was validation-only and available release tooling was dry-run/non-releasing.
4. Failure, rollback, remediation, and post-action verification controls were missing.

Evidence Existing Before Mini-EPIC 32.148

The repository already contained:

- approved repository/source identity `ahabibian/InvoMatch` at `6c4b3c3e35798de945a3219bbd419d4f6e41d8b7`;
- successful exact-source validation run `32487366423`;
- backend product version `0.1.0` in `pyproject.toml` and the runtime release identity model;
- a private frontend package version `0.0.0`, which is build-tool metadata and not an independently publishable product version;
- a future release-package manifest contract;
- a historical local package for different source SHA `e1f1a943322787db2a55b1fc3b12ec8c9fe5d6a1`, which remains ineligible for reuse;
- a dry-run manifest-preview script that explicitly performs no release mutation; and
- no Git tags and no repository-controlled GitHub Release workflow.

Evidence Introduced by Mini-EPIC 32.148

Mini-EPIC 32.148 adds:

- `docs/architecture/CANONICAL_RELEASE_SUBJECT_0_1_0.json`, a canonical deterministic subject manifest;
- `scripts/canonical_release_preflight.py`, a non-mutating subject and repository-state preflight;
- focused regression tests for deterministic identity, mismatch rejection, duplicate/conflict handling, and workflow safety;
- `.github/workflows/canonical-release-preflight.yml`, a manually invoked, read-only preflight workflow; and
- full-history checkout in the validation workflow so tests can reproduce evidence from the exact approved historical source object; and
- the failure, abort, remediation, idempotency, and verification contracts recorded here.

Release Subject Identity

The canonical subject manifest binds:

- repository: `ahabibian/InvoMatch`;
- approved source branch: `main`;
- approved source SHA: `6c4b3c3e35798de945a3219bbd419d4f6e41d8b7`;
- release version: `0.1.0`;
- required tag identity: `v0.1.0`;
- deterministic package ID: `invomatch-0.1.0-source-6c4b3c3e3579`;
- deterministic package filename: `invomatch-0.1.0-source-6c4b3c3e3579.tar`;
- package construction: repository-controlled `deterministic-git-tree-tar-v1` encoding of the exact approved Git tree, with sorted paths and fixed metadata;
- package SHA-256: `f7e8f394d6bc41b63bb9e39e8abf86f8d32820b9774b2a24d1a01ca15b8d2b84`;
- package size: `6318080` bytes;
- frontend dependency-lock SHA-256: `d4c6f5f6e74cd45bf143488dff19a5318d4119426f78e6a2dd5f39912c00ef1a`;
- CI configuration SHA-256: `030a71a32c0cd7f90b40377797678f298741932d9df6617b91f2ad5c481783b2`;
- build identity: GitHub Actions run `32487366423`; and
- canonical manifest identity SHA-256: `51e1393476197d07799248c93dc0b2325f26b7d711f206e0d7668852f9177f45`.

The package is a reproducible on-demand identity product. Mini-EPIC 32.148 does not commit, publish, distribute, or upload the archive.

Version, Manifest, and Digest Model

Version `0.1.0` is derived from the repository's product authority at the approved source: `pyproject.toml [project].version`, which matches the runtime default application version. The private frontend package version is explicitly classified as tool-package metadata rather than the canonical product release version.

The manifest identity digest is calculated over canonical sorted compact JSON excluding the digest container itself. The preflight regenerates the source archive directly from the approved Git object using a repository-controlled tar encoder with sorted Git-tree paths, zero timestamps, fixed ownership, and normalized Git-derived modes. It independently verifies version, tag syntax, archive digest and size, dependency lock digest, CI workflow digest, action category, and manifest identity digest.

Any mismatch fails closed. No timestamp, working-directory order, filesystem metadata, or mutable local output is used as subject authority.

Actor and Process Authority

Mini-EPIC 32.148 establishes the repository-controlled actor model:

- preflight actor: manually invoked GitHub Actions workflow `Canonical release preflight`;
- future authorization evaluator: a separately controlled canonical governance boundary;
- future execution actor, if separately authorized: repository-controlled GitHub Actions using the GitHub-provided token for the bounded compound tag-if-absent and GitHub Release creation action; and
- no individual user identity, personal token, secret, or credential is invented.

The read-only workflow continues to implement preflight only. A separate manual execution workflow now represents the future operation, but fails closed unless exact later authorization and canonical subject inputs are supplied. Mini-EPIC 32.148 does not invoke it.

Permission Boundary

The added preflight workflow has only:

`contents: read`

It is manual `workflow_dispatch` only and has no push or pull-request trigger. It cannot create tags, releases, artifacts, deployments, or promotions.

The separate future execution workflow defaults to `contents: read` and grants the narrow `contents: write` permission only to its execution job. It is not added to normal CI or the standalone preflight workflow. No broader administrative permission is defined.

Operational Capability Evidence

The preflight mechanism can safely represent and verify the release subject and conflict model without mutation. It provides:

- exact manifest input;
- version and tag syntax verification;
- source SHA resolution;
- deterministic archive regeneration and digest verification;
- dependency-lock and configuration verification;
- action-category verification;
- absent-tag detection;
- conflicting-tag detection;
- fresh-release versus exact-replay classification; and
- fail-closed exit behavior.

The future creation mechanism is `gh release create` in the separately authorized repository-controlled workflow. The mechanism is implemented as capability evidence but is not called by Mini-EPIC 32.148.

Repository policy contains no authoritative requirement that `v0.1.0` pre-exist. GitHub Release creation supports creating a missing tag at an exact `target_commitish` or `--target` SHA. The canonical action is therefore one bounded compound operation: create tag `v0.1.0` if absent at approved SHA `6c4b3c3e35798de945a3219bbd419d4f6e41d8b7`, then create GitHub Release `v0.1.0`. Existing mismatched tag or release state fails closed.

Platform capability authority:

- GitHub CLI `gh release create`: https://cli.github.com/manual/gh_release_create
- GitHub REST API create-release `target_commitish`: https://docs.github.com/en/rest/releases/releases#create-a-release

Dry-Run and Preflight Behavior

The local preflight completed successfully for subject identity and printed `subject-identity-verified` with the expected evidence.

The manual workflow runs the same command with read-only permissions. It performs no GitHub mutation.

Repository-state preflight accepts an absent tag as valid pre-mutation state for the compound action. It fails on a tag targeting a different source SHA, a release without matching tag evidence, or a release whose target or manifest identity conflicts. An exact existing release is classified as an exact replay rather than overwritten.

Failure, Abort, Rollback, and Remediation Contract

Pre-execution abort

Future execution must stop before mutation for any source, version, tag, manifest, digest, dependency-lock, configuration, validation, authorization, permission, capability, duplicate, or target mismatch. An absent tag is permitted only as the expected input to the bounded tag-if-absent operation.

Partial failure

The future action is the bounded compound tag-if-absent plus GitHub Release creation operation. If automatic tag creation succeeds but GitHub Release creation fails, the tag must not be deleted automatically; evidence is captured and separately remediated. If future artifact attachment is separately authorized and an upload fails after release creation, the release must be marked or documented incomplete and routed to remediation; public evidence must not be silently deleted.

Rollback and remediation

Automatic deletion of tags or public releases is prohibited. Reversal of a public object requires a separate explicit remediation authority. A failed create with no object created is safely retryable after the cause is corrected. A partially created or conflicting object requires evidence capture and a separately controlled remediation decision.

Post-creation verification

A future execution must verify the tag target SHA, version/tag, GitHub Release existence, repository target, expected metadata, manifest identity, and any separately authorized artifact/digest correspondence. Verification evidence must record the API result and immutable identifiers without exposing credentials.

Idempotency and Conflict Handling

- Absent tag and absent release: eligible for the bounded compound operation after separate authorization.
- Existing tag at another SHA: conflict; abort.
- Existing tag at the approved SHA with no release: eligible for fresh authorization review only.
- Existing release at another subject or manifest identity: conflict; abort without overwrite.
- Exact replay of an already successful release: report already complete; do not create or overwrite.
- Mismatched version or subject: abort and require new canonical evidence.

Validation Evidence

Mini-EPIC 32.148 validates:

- deterministic subject evidence across repeated preflight construction;
- exact source binding;
- archive and manifest digest verification;
- source, digest, and version mismatch rejection;
- absent and conflicting tag handling;
- fresh release and exact replay distinction;
- manual-only workflow triggering;
- read-only workflow permissions;
- absence of release mutation commands; and
- separate future execution workflow authorization gating, job-scoped write permission, exact target command, conflict handling, and post-action verification; and
- non-mutating local preflight success.

Full repository validation results are recorded in the closure after execution.

Re-evaluated Blocker Matrix

Release-subject identity: remediated.

Actor/process model: remediated. Read-only preflight remains separate; the future manual execution workflow is authorization-gated and uses repository-controlled GitHub Actions.

Failure/rollback/remediation/verification contract: remediated as a governance contract.

Operational capability: remediated. The future workflow is manual only, has job-scoped `contents: write`, verifies authorization, exact source, version, tag, manifest identity and digests, rejects conflicts, performs the bounded `gh release create v0.1.0 --target <approved SHA>` operation, and verifies the resulting tag and release. It is not invoked by Mini-EPIC 32.148.

Remediation Outcome

All four Mini-EPIC 32.147 blocker classes are now resolved for fresh authorization re-evaluation. Mini-EPIC 32.148 selects:

CANONICAL_RELEASE_AUTHORIZATION_BLOCKERS_REMEDIATED

READY_FOR_CANONICAL_RELEASE_EXECUTION_OR_PUBLICATION_GOVERNANCE_AUTHORIZATION_REEVALUATION_BOUNDARY

Mini-EPIC 32.148 does not emit authorization success or execution readiness.

Forward Boundary

The exact next boundary is Mini-EPIC 32.149 — Canonical Release Execution or Publication Governance Authorization Re-Evaluation Boundary. It may evaluate authorization but must not execute the future workflow.

Operational Non-Actions

Mini-EPIC 32.148 preserves:

- no authorization success;
- no execution readiness;
- no tag creation;
- no tag push;
- no GitHub Release creation;
- no artifact publication;
- no artifact distribution;
- no deployment;
- no staging promotion;
- no production promotion;
- no CI release execution;
- no externally visible publication;
- no customer-facing activation;
- no historical authority restoration;
- no historical Mini-EPIC 32.134 approval adoption; and
- no historical Mini-EPIC 32.135 through 32.140 authority adoption.

Historical Separation

Historical Mini-EPICs 32.128 through 32.140 remain non-authoritative. Historical `FINAL_RELEASE_READINESS_APPROVED` remains non-canonical. Historical release/publication authorization and execution outcomes are not reused.

Boundary Result

Mini-EPIC 32.148 records only:

CANONICAL_RELEASE_AUTHORIZATION_BLOCKERS_REMEDIATED

READY_FOR_CANONICAL_RELEASE_EXECUTION_OR_PUBLICATION_GOVERNANCE_AUTHORIZATION_REEVALUATION_BOUNDARY

Subject identity, actor/process authority, operational capability, and failure/remediation/post-verification controls are established. Authorization has not been re-issued and no public mutation occurs.
