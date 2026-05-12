# Architecture

## Product purpose
Deepshield is a multi-tenant SaaS platform for collecting security-relevant signals, normalizing them into durable evidence, analyzing them for risk patterns, and routing actionable alerts to responders. The MVP favors traceability and deterministic processing over broad connector coverage, so every alert can be explained from source event to analyst-facing incident.

## SaaS tenant model
- **Tenant isolation**: every record is scoped by `tenant_id` at ingest, storage, analysis, and query time.
- **Logical data partitioning**: tenant data lives in shared services but is isolated via row-level access constraints and per-tenant encryption context.
- **Identity boundaries**: users belong to one or more tenants through explicit memberships and role assignments.
- **Role model (MVP)**:
  - `owner`: manages tenant settings, users, and retention.
  - `analyst`: investigates alerts/incidents and labels outcomes.
  - `viewer`: read-only access to dashboards and audit reports.
- **Configuration inheritance**: global defaults exist, but tenant-level policies override thresholds, suppression rules, and notification routes.

## Evidence lifecycle
1. **Ingestion**: source systems submit events through API/webhook connectors.
2. **Validation**: schema and authentication checks reject malformed/unauthorized payloads.
3. **Normalization**: source-specific fields are transformed into canonical evidence types.
4. **Enrichment**: optional metadata (asset owner, geo, reputation, user directory tags) is attached.
5. **Persistence**: raw payload + canonical envelope are stored with immutable timestamps.
6. **Retention/expiry**: records remain queryable per tenant policy and are archived/purged on schedule.
7. **Replay support**: retained evidence can be re-queued to newer analyzer versions for backtesting.

## Analyzer pipeline
- **Stage A — Pre-filter**: deduplication, suppression checks, and severity floor.
- **Stage B — Rule execution**: deterministic rules evaluate canonical evidence against tenant policy.
- **Stage C — Correlation**: short time-window joins group related evidence into candidate incidents.
- **Stage D — Scoring**: heuristic risk score combines rule confidence, asset criticality, and burst behavior.
- **Stage E — Decision**: emit alert, append to open incident, or mark as informational.
- **Pipeline guarantees (MVP)**:
  - at-least-once processing;
  - idempotent alert keys to reduce duplicate incidents;
  - versioned rule/analyzer metadata attached to outputs for explainability.

## Alert/incident flow
1. Analyzer emits an alert candidate.
2. Routing policy chooses destination channels (in-app queue, email, webhook).
3. Incident service either links to an existing open incident (same correlation key) or creates new.
4. Analysts triage (`new -> investigating -> mitigated` or `false_positive`).
5. Incident timeline is updated with comments, ownership changes, and evidence attachments.
6. Closure stores resolution reason and optional follow-up tasks.

## Audit trail
- Every mutable action (policy edits, triage state changes, user/role updates, suppressions) writes an append-only audit entry.
- Audit entry fields:
  - actor (`user_id` or service principal),
  - tenant,
  - action type,
  - target object,
  - before/after snapshot (redacted as needed),
  - request metadata (time, IP, user agent, request id).
- Audit records are immutable, queryable by compliance filters, and exportable in CSV/JSON.

## Deployment design
- **Frontend**: SPA served via CDN.
- **Backend API**: stateless service handling auth, tenancy, policy, query, and incident endpoints.
- **Ingestion workers**: horizontally scalable consumers for connector traffic and normalization.
- **Analyzer workers**: asynchronous processors that execute rules/correlation/scoring.
- **Data layer**:
  - relational DB for tenant config, incidents, and audit indices;
  - object/blob storage for raw evidence payloads;
  - queue/stream bus between ingest and analyzer stages;
  - cache for session and hot incident lookups.
- **Operations**: centralized logs, metrics, and tracing with per-tenant dimensions.

## Current limitations
- Connector set is intentionally narrow (core webhook/API ingest only).
- Rule engine is deterministic; no ML model inference in the critical path.
- Cross-tenant benchmarking and global threat intel sharing are not enabled.
- High-availability posture is best-effort (single-region MVP assumptions).
- Notification routing is limited to core channels; no on-call escalation orchestration.
- Evidence replay and backfill tooling exist conceptually but may require operator-assisted runs.

## Future production requirements
- Multi-region active/passive or active/active design with tested failover RTO/RPO.
- Stronger tenant isolation options (dedicated data planes / per-tenant keys via KMS).
- Formal data classification, DLP controls, and field-level encryption for sensitive evidence.
- Policy-as-code version workflows with approvals and rollout gates.
- Expanded connector marketplace and robust schema registry/version migration tools.
- Advanced incident automation (playbooks, SOAR integrations, ticketing sync).
- SLO-backed observability and autoscaling tied to ingest/analyzer queue health.
- Comprehensive disaster recovery, load testing, and compliance evidence packs (SOC 2, ISO 27001 controls mapping).
