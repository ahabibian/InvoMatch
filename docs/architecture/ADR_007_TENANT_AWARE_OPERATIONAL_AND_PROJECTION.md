Title:

Tenant-Aware Operational Layer and Projection Strictness



Context:

Recent changes introduced tenant\_id requirement across:

\- Operational audit events

\- Startup repair metrics

\- Recovery loop



Additionally, finalized projection now requires:

\- created\_from\_run\_version

\- source\_fingerprint



Decision:

1\. All operational events are tenant-scoped

2\. Operational boundary uses default tenant:

&#x20;  "operational-boundary" when not explicitly provided

3\. Finalized projections are strictly versioned and cannot be created without version linkage

4\. Product run view for completed runs reads ONLY from projection (not run.report)



Consequences:

\- Improved audit safety and multi-tenant isolation

\- Stronger projection immutability

\- Breaking change in test expectations (run\_view match summary)



Risks:

\- Incomplete tenant propagation across all operational services

\- Potential mismatch between report and projection if projection not built

