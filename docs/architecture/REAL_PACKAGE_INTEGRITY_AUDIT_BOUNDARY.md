Real Package Integrity Audit Boundary
Mini-EPIC: 32.81 — Real Package Integrity Audit Boundary Definition
Status: Defined
Branch: main
Source commit at definition time: 738251bef6edfb76854ff1f2e566059494a7ff90
1. Purpose
This document defines the boundary for a future real package integrity audit.
The purpose of this mini-epic is only to define what the future integrity audit must verify before any package acceptance, release approval, publication, deployment, or environment promotion.
This document does not approve any package.
This document does not execute the integrity audit.
This document does not publish, deploy, release, promote, or make any package customer-facing.
2. Governance Boundary
The integrity audit boundary is a verification boundary only.
It may define required checks for a future audit, but it must not make an acceptance decision.
The following actions remain explicitly out of scope:


Approving a package


Accepting a package as release-ready


Publishing a package


Creating a GitHub release


Creating or pushing a release tag


Deploying to staging


Deploying to production


Promoting any environment


Marking any artifact as customer-facing


Mutating package contents


Rebuilding the package during audit


Treating local package existence as release approval


Any future package acceptance decision must be handled in a separate governed mini-epic with explicit evidence and authorization.
3. Audit Object Boundary
A future integrity audit must identify the exact package and manifest under review.
The audit must record:


Package path


Manifest path


Package filename


Manifest filename


Package size


Manifest size


Package hash


Manifest hash


Source commit SHA declared by the manifest


Current repository commit SHA at audit time


Current branch at audit time


Working tree state at audit time


Audit timestamp in UTC


Audit command or method used


The audit must not rely on vague references such as "latest package", "current package", or "the package from last run".
4. Package Hash Verification
A future integrity audit must compute and record a cryptographic hash for the real package.
The package hash verification must confirm:


The package file exists at the governed local output path


The package is readable


The computed package hash is captured in the audit evidence


The hash algorithm is explicitly named


The hash value is stable across repeated reads of the same file


The manifest references the same package identity, if a package hash field exists in the manifest


Any mismatch between computed hash and manifest-declared hash blocks package acceptance


If the manifest does not currently include a package hash field, the audit must record that limitation explicitly instead of silently assuming integrity.
5. Manifest Consistency Verification
A future integrity audit must verify that the real package manifest is internally consistent.
The manifest consistency check must verify:


The manifest file exists


The manifest is valid JSON if stored as JSON


The manifest has the expected schema version


The manifest is not a dry-run preview manifest


The manifest does not claim publication, deployment, production readiness, or customer availability


The manifest package identity matches the package under audit


The manifest source identity is present and non-ambiguous


The manifest included components section is present


The manifest excluded components section is present


The manifest reproducibility metadata section is present


The manifest non-publication or non-deployment boundary section is present


The manifest evidence references point to governed documentation and not to ad hoc local notes


Any missing, malformed, contradictory, or over-claiming manifest section must block package acceptance.
6. Included Component Verification
A future integrity audit must verify that the package contains only the components expected by the governed package creation procedure.
The included component verification must check:


Backend source components expected for the package


Frontend source or build components expected for the package


Project configuration files expected for reproducibility


Required architecture or release documentation expected to be included


Required manifest or metadata files expected to be included


Any explicitly declared evidence references included in the package


The audit must compare the actual package contents against the manifest included components list.
The audit must record whether every declared included component is present.
The audit must record whether the package contains any extra component not declared by the manifest.
Unexpected included files must not be accepted silently.
7. Excluded Component Verification
A future integrity audit must verify that excluded components are absent from the package.
The excluded component verification must check at minimum for absence of:


Local runtime databases


SQLite database files


Local runtime artifacts


Dependency caches


Python cache directories


Node dependency directories


Test cache directories


Temporary package outputs


Previous package outputs


Local-only preview outputs


Editor state files


Operating system metadata files


Secret files


Environment files


Private credentials


Token files


CI secrets


Deployment credentials


Customer data


Tenant data


Uploaded user files


Generated logs


Local debug artifacts


The audit must compare the actual package contents against the manifest excluded components list.
Any forbidden or excluded file found inside the package must block package acceptance.
8. Forbidden File Boundary
A future integrity audit must include an explicit forbidden-file scan.
The forbidden-file scan must check for patterns including but not limited to:


.env


.env.*


*.db


*.sqlite


*.sqlite3


*.pem


*.key


*.p12


*.pfx


id_rsa


id_ed25519


secrets.*


credentials.*


token.*


*.log


pycache/


.pytest_cache/


node_modules/


.venv/


venv/


dist/ when not explicitly expected


build/ when not explicitly expected


output/local/


package preview outputs


temporary release working folders


The audit must not depend only on the manifest declaration.
The package contents themselves must be inspected.
9. Source Commit Alignment
A future integrity audit must verify source commit alignment.
The audit must compare:


Manifest-declared source commit SHA


Current repository HEAD SHA at audit time


Package creation evidence source commit SHA


Any recorded closure commit from the package creation mini-epic


Any source identity embedded in package metadata


The audit must clearly distinguish between:


The commit used to create the package


The commit used to define the audit boundary


The commit used to run the future audit


The commit used to make any future acceptance decision


A package must not be accepted if its source identity is ambiguous, missing, contradictory, or not aligned with the governed package creation evidence.
10. Working Tree and Repository State Expectations
A future integrity audit must record repository state at audit time.
The audit must verify:


Current branch


Current HEAD commit


Working tree status


Whether the tree is clean or dirty


Whether package files are tracked, untracked, or intentionally local-only


Whether generated package outputs are excluded from source control as expected


Whether audit evidence is tracked in documentation only


A dirty working tree does not automatically prove package corruption, but it must block acceptance unless explicitly explained and governed.
11. Reproducibility Metadata Verification
A future integrity audit must verify reproducibility metadata.
The audit must check whether the manifest records:


Source commit SHA


Source branch


Package creation timestamp


Package creation procedure reference


Package creation mini-epic reference


Tooling or command used to create the package


Relevant runtime assumptions


Python version assumptions, if applicable


Node/npm version assumptions, if applicable


Dependency reproducibility limitations


Known non-determinism or unpinned dependency risks


Evidence references for validation gates


If reproducibility metadata is incomplete, the audit must record the gap explicitly.
Incomplete reproducibility metadata blocks package acceptance unless a separate acceptance decision explicitly accepts that risk.
12. Evidence Reference Consistency
A future integrity audit must verify that manifest evidence references are consistent with governed repository documentation.
The audit must check references to:


EPIC 32 release pipeline documentation


Package creation authorization decision record


Package creation procedure


Package creation procedure review


Package creation pre-execution readiness check


Controlled real package creation execution record


Post-execution repository and local output sanity audit


This integrity audit boundary definition


Any future integrity audit execution record


Any future package acceptance decision record


Evidence references must not imply that a package is approved unless a separate acceptance decision exists.
13. Non-Publication and Non-Deployment Boundary Verification
A future integrity audit must verify that the package remains inside the non-publication and non-deployment boundary.
The audit must confirm that no action occurred in the integrity audit that:


Publishes the package


Uploads the package to a public registry


Uploads the package to a customer-facing system


Creates a GitHub release


Creates a release tag


Builds or pushes a container image


Deploys to staging


Deploys to production


Promotes any environment


Writes release state into a production system


Marks the package as accepted


Marks the package as release-ready


Marks the package as production-ready


The audit may verify local package integrity only.
14. Acceptance Boundary
Integrity verification and acceptance decision-making are separate.
A successful integrity audit may support a future acceptance decision, but it is not itself acceptance.
The following statements are forbidden inside the integrity audit unless a separate acceptance mini-epic has already made the decision:


Package approved


Package accepted


Release approved


Ready for production


Ready for customer use


Published


Deployed


Promoted


Production release complete


The integrity audit may only state whether defined integrity checks passed, failed, or were not applicable.
15. Required Future Audit Result Shape
A future integrity audit should produce a structured result with at least:


Audit status: passed, failed, or blocked


Package identity


Manifest identity


Source identity comparison


Hash verification result


Manifest consistency result


Included component verification result


Excluded component verification result


Forbidden file scan result


Reproducibility metadata result


Evidence reference consistency result


Non-publication boundary result


Known limitations


Blocking issues


Non-blocking observations


Explicit statement that no acceptance, release, publication, deployment, or promotion occurred


A passed integrity audit still must not approve the package.
16. Exit Criteria for Mini-EPIC 32.81
This mini-epic is complete when:


This boundary document exists under docs/architecture


EPIC_32_RELEASE_PIPELINE.md references this boundary


A closure document records the result


The closure document confirms no package approval occurred


The closure document confirms no release, deployment, publication, or promotion occurred


The repository is committed cleanly


17. Final Boundary Statement
Mini-EPIC 32.81 defines the real package integrity audit boundary only.
It does not execute the audit.
It does not approve the package.
It does not release, publish, deploy, or promote anything.
