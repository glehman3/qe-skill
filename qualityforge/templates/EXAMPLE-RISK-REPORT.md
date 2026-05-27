<!--
NOTE:
This example demonstrates the lean Quality Risk Analysis format.
Evidence is embedded inline in descriptions, not in separate blocks.
Rubric: qualityforge/risk/CONTENT-ACCURACY-RUBRIC.md
-->

## Quality Risk Analysis: SMS Scheduling Feature (Example)

**Generated:** 2026-01-08  
**Repository:** `org/project`  
**PRD:** [SMS Scheduling Feature PRD](https://confluence.example.com/display/MAIL/SMS-Scheduling-PRD)  
**Jira:** TXPLAT-5432 *(optional)*

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Risks** | 4 |
| 🔴 Critical | 2 |
| 🟠 High | 1 |
| 🟡 Medium | 1 |
| 🟢 Low | 0 |
| **Codebase Touch Points** | ~5 files across 2 services |
| **Recommended Spikes** | 2 |

### Top 3 Concerns
1. Adding scheduling fields to the send API may break existing consumers if not versioned.
2. Data model changes require a migration strategy — no rollback plan exists yet.
3. Retry logic without idempotency could cause duplicate SMS sends.

### Key Requirements
- REQ-001: User can schedule an SMS to be sent at a future time
- REQ-002: Scheduled messages can be cancelled before send
- REQ-003: System must reliably deliver scheduled messages with retries
- REQ-004: No breaking changes for existing API consumers (preferred)

---

## Codebase Touch Points

| Area | Risk | Why |
|------|:----:|-----|
| `src/api/messages/send.js` | 🔴 | Scheduling requires new fields on send endpoint |
| Message model / DB schema | 🔴 | New columns for schedule time, status, cancellation |
| Scheduler service (new) | 🟠 | New job runner for timed delivery + retries |
| Monitoring / dashboards | 🟡 | No observability for schedule lifecycle today |

**External Dependencies:** SMS provider API (rate limits, delivery callbacks), job queue infrastructure

---

## Risks

### 🔴 Critical

#### RISK-001: Breaking API change for message sending
The PRD requires scheduling fields on the send endpoint (REQ-001), but the existing `/messages/send` handler (CODE-001) has active consumers. If the contract changes without versioning, downstream services will break. The PRD prefers no breaking changes (REQ-004) but scheduling inherently adds new required fields. **Confidence: Medium** — consumer list not yet enumerated.

**Mitigations:**
1. Add a versioned endpoint (`/v2/messages/send`) for scheduling support
2. Publish an ADR + consumer migration plan with timeline and ownership

---

#### RISK-002: Data model migration risk
Scheduling requires persistent fields — schedule time, status, cancellation metadata (REQ-001, REQ-002). The Message model exists (CODE-002) but has no migration plan for adding these columns. Without a verified rollback strategy, production deployment is risky. **Confidence: Low** — storage approach (same table vs. separate store) not decided yet.

**Mitigations:**
1. Use expand/contract schema approach (add nullable columns, deploy, backfill, enforce)
2. Define rollback plan and test on staging with production-scale data

---

### 🟠 High

#### RISK-003: Duplicate sends from retry logic
The system must reliably deliver with retries (REQ-003), and scheduler/job patterns exist in the codebase (CODE-003). Retries without idempotency keys will cause duplicate SMS sends — a poor user experience and potential compliance issue. **Confidence: Medium** — retry infrastructure exists but idempotency not confirmed.

**Mitigations:**
1. Implement idempotency key per scheduled message
2. Add dead-letter handling for failed retries with alerting

---

### 🟡 Medium

#### RISK-004: No observability for scheduled send lifecycle
Reliable delivery (REQ-003) implies monitoring and alerting, but existing logging conventions (CODE-004) don't cover the new schedule lifecycle. Without dashboards for schedule success rate, backlog depth, and delivery latency, production debugging will be slow. **Confidence: Low** — current observability coverage not verified.

**Mitigations:**
1. Define SLOs and create dashboards before launch
2. Add structured logging for schedule lifecycle events (created, fired, succeeded, failed)

---

## Open Questions

### Blockers (P0)
- Which services/clients consume the `/messages/send` endpoint today?
- Where is the source of truth for scheduling state — message record or separate store?

### High Priority (P1)
- What is the current observability standard for message sends?
- Does the SMS provider support delivery status callbacks?

---

## Recommended Spikes

| Spike | Why | Success Criteria | Est. Time |
|-------|-----|------------------|-----------|
| Enumerate API consumers | Versioning strategy depends on consumer count | Consumer list + migration approach documented | 1 day |
| Schema migration prototype | Need rollback plan before production deploy | Proposed schema + rollout/rollback steps tested | 2 days |

---

## Sources

- PRD: https://confluence.example.com/display/MAIL/SMS-Scheduling-PRD
- Jira: TXPLAT-5432
