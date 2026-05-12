# MVP Scope vs v3 Target

## Scope intent
This document defines what is **in** the current MVP, what is explicitly **out**, and the staged path to a v3 production-ready platform. It aligns product expectations with concrete backend/frontend implementation boundaries.

## Current MVP boundaries

### In-scope (MVP)
- Tenant-aware authentication and role-based access (`owner`, `analyst`, `viewer`).
- API/webhook ingestion with canonical evidence normalization.
- Deterministic rule-based analysis and basic correlation windowing.
- Alert queue and incident lifecycle management in the web app.
- Core audit logging for security-sensitive user and system actions.
- Basic notification channels (in-app + minimal external channels such as email/webhook).

### Out-of-scope (MVP non-goals)
- Full SOAR orchestration and automated response execution.
- ML-driven anomaly detection in real-time decision path.
- Broad connector ecosystem and self-service connector builder.
- Multi-region active/active resiliency with strict uptime SLAs.
- Enterprise governance features (fine-grained legal holds, advanced eDiscovery).
- Cross-tenant intelligence sharing or benchmarking analytics.

## v3 target boundaries

### In-scope by v3
- Expanded connector catalog with versioned schema governance.
- Policy-as-code workflow with review/approval and staged rollouts.
- Advanced incident workflows (escalation policies, ticketing/chat integrations, runbooks).
- Replay/backtesting UI for analyzer/rule changes.
- Multi-region resiliency, mature SLOs, and hardened operational controls.
- Compliance reporting packs and audit export automation.

### Still out-of-scope by v3 (unless strategy changes)
- Fully autonomous remediation agents without human approval gates.
- Consumer-grade freemium feature set and mass-market onboarding flows.
- Arbitrary custom compute in tenant-owned runtime sandboxes.

## Assumptions
- Tenants accept logical (not physical) isolation in MVP.
- Early adopters prioritize explainability and auditability over detector sophistication.
- Security operations teams can tolerate manual triage load until automation matures.
- Integration demand is concentrated in a small set of high-value event sources first.
- Product and engineering can sequence platform hardening after proving core incident value.

## Staged implementation roadmap

### Stage 1 — MVP foundation (current)
**Backend changes**
- Implement tenant-scoped authZ in all APIs.
- Build ingestion endpoint, validator, canonical evidence store.
- Deliver rule engine v1 + simple correlation and incident persistence.
- Emit audit events for auth, policy changes, and triage actions.

**Frontend changes**
- Tenant switch/access gating UX.
- Alerts list, incident detail page, triage status transitions.
- Basic policy configuration and audit log views.

### Stage 2 — Operational hardening
**Backend changes**
- Add queue durability improvements, idempotency enforcement, replay tooling.
- Introduce richer notification routing and suppression windows.
- Expand observability (SLO metrics, analyzer latency, dropped-event counters).

**Frontend changes**
- Incident timeline enhancements and richer filtering/search.
- Notification routing management UI.
- Health/status dashboard for ingest + analyzer pipeline.

### Stage 3 — v3 readiness
**Backend changes**
- Policy-as-code APIs with version history and approvals.
- Connector framework with schema registry/version migrations.
- Multi-region deployment support and DR automation hooks.
- Compliance export/report generation services.

**Frontend changes**
- Rule/policy version comparison, approval workflow, rollout controls.
- Connector catalog and tenant-level connector lifecycle screens.
- Replay/backtesting interface with outcome diffs.
- Compliance reporting workspace and scheduled exports.

## Dependency links (backend ↔ frontend)
- **Incident workflow UX depends on** backend incident state machine and audit events.
- **Policy editor UX depends on** backend rule schema validation and version APIs.
- **Pipeline health dashboard depends on** backend observability metrics endpoints.
- **Replay/backtesting UI depends on** backend evidence replay job orchestration and result storage.
- **Compliance reporting UI depends on** backend export jobs and signed artifact access.

## Exit criteria

### MVP exit criteria
- End-to-end flow from ingest -> analysis -> alert -> incident triage is production-usable for pilot tenants.
- All tenant-facing actions are access-controlled and auditable.
- Core failure modes are observable and operationally recoverable.

### v3 exit criteria
- Platform supports enterprise rollout with documented resiliency, compliance, and governance controls.
- Rule/policy lifecycle and connector lifecycle are managed, versioned, and testable.
- Incident operations scale with automation assist and deep integration points.
