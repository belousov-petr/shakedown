# Deep Project Audit — AI News Intelligence Pipeline

**Audit date:** 2026-04-10
**Methodology:** deep-project-audit v1.0.0 (6-phase structured audit)
**Auditor:** Claude Opus 4.6

> **Note:** This is an anonymized audit of a real project. Organization names,
> agent UUIDs, file paths, API keys, database credentials, and personal
> identifiers have been replaced with generic placeholders.

---

## 4.1 What the Project Is

A daily AI news intelligence pipeline built on Paperclip (an agent
orchestration platform). 16 AI agents — 9 domain-specific scouts, a
scout lead, a senior analyst, an editor, a coordinator, an auditor, a
report designer, and an email dispatcher — run autonomously on a
weekday schedule. The pipeline discovers AI-related signals from web
sources across 9 domains (industry deployments, regulation, incidents,
competition, frontier research, published reports, criticism,
sovereignty, and local ecosystem), deduplicates them, scores by
priority, and produces a daily intelligence brief. Storage is hybrid:
file-based JSON signals (~470 signal files) + embedded PostgreSQL for
analytics. Runs on a local machine with a VPS migration planned.

---

## 4.2 What Works Well

**Event-driven pipeline with clear handoffs.** Scouts fire in parallel
at 01:00 CET. When all complete, Scout Lead triggers automatically
(event-driven, not polled). Scout Lead completes, Senior Analyst
triggers. Senior Analyst completes, Editor triggers. No manual
orchestration needed. End-to-end: ~30 minutes.

**Evidence:** OPS.md documents the full pipeline flow. 8 daily briefs
produced in the last 11 days (gap on Apr 5-8 due to incident recovery).

**Domain-specific agent instructions are well-scoped.** Each scout has
clear domain boundaries, explicit source lists, keyword tiers, and
handoff rules ("not this scout's domain — goes to X"). This prevents
duplicate signals from overlapping scouts.

**Evidence:** Agent instruction files include "Domain boundaries" and
"NOT this scout's domain" sections.

**Operations runbook is thorough.** OPS.md covers architecture,
timeout configuration, incident playbook (stuck runs, missing briefs,
auth expiry), file locations, agent IDs, session history, and known
issues. This is the kind of operational documentation most projects
never write.

**Timeout configuration after incident.** After a 9-hour stuck run,
all 15 agents were configured with timeout limits (20-30 min). The
platform sends SIGTERM at timeout and SIGKILL after 20s grace period.

**VPS migration planned.** A detailed migration guide covers server
setup, data export/import, database migration, secrets management,
systemd service configuration, and post-migration validation. 80%
complete.

---

## 4.3 Critical Issues

**1. Duplicate agent exists and needs deletion.** The Pipeline Auditor
agent was duplicated at some point. The duplicate has its own UUID and
instruction files but serves no purpose. It's listed as P0 in the known
issues but hasn't been removed.

**Impact:** Potential for the wrong auditor instance to be triggered,
producing invalid or missing audits.

**2. No timeout incident reporting.** When an agent times out, the
platform kills the process but doesn't generate a diagnostic report.
The operator discovers failures only by manually checking the UI or
noticing a missing daily brief. A spec for timeout incident reporting
has been written (in Claude memory) but not implemented.

**Impact:** Silent failures. The 9-hour stuck run was discovered by
accident, not by alerting.

**3. Zero automated tests.** No test files, no test framework, no CI.
The pipeline is a 16-agent system with complex coordination running
autonomously — untested.

**Evidence:** No `tests/` directory. No pytest/jest configuration.
Listed as P2 in known issues (should arguably be P1 for a system that
runs unattended daily).

---

## 4.4 Architecture & Code Quality

**Structural analysis:**

| Aspect | Assessment |
|--------|-----------|
| Storage model | Hybrid: file-based JSON signals (source of truth) + PostgreSQL (analytics). Good separation — filesystem survives DB corruption, DB enables querying. |
| Pipeline flow | Event-driven chain: scouts (parallel) → lead → analyst → editor. Clean, no polling. |
| Sequential bottlenecks | Scouts run in parallel (good). But lead/analyst/editor run sequentially (necessary — each depends on prior output). |
| Single points of failure | Claude CLI auth — if subscription expires, all agents fail. Cookie file for scouts' web access. Single local machine (until VPS migration). |
| Scalability | 9 scouts cap at 4 signals/run each = 36 max signals/day. At current volume (~30/day), this is near capacity. Adding more scouts scales linearly. |

**Design pattern coherence:** Consistent — all agents follow the same
pattern: AGENTS.md instructions, file-based I/O through Paperclip's
signal directories, event-driven triggers. No drift.

**MECE check:**
- **Overlap:** Industry Scout and Netherlands Scout have potential
  overlap on Dutch AI company news. Resolved by explicit domain
  boundaries in instructions ("NL-specific company news goes to
  Netherlands Scout").
- **Gap:** No agent monitors pipeline health in real-time. The Pipeline
  Auditor runs weekly (Saturday/Sunday), not daily. Between audits,
  failures go undetected.
- **Gap:** No agent handles signal archival or cleanup. Signals
  accumulate indefinitely (470+ files and growing).

**Code quality:**
- Agent instructions are well-written: clear, scoped, with examples.
- Several artifact files in the project root (`2`, `5`, `8)`,
  `{assignee}`, `'maxTurnsPerRun'`) — likely accidental CLI output
  written to disk. Harmless but messy.
- Operations documentation (OPS.md, VPS-MIGRATION.md) is thorough.
- PROJECT-MEMORY.md is stale — says 12 agents when actual count is 16.

**Test coverage:** None. Zero automated tests for any component.

---

## 4.5 Error Handling, Resilience & Failure Modes

**Crash scenarios:**
- **Agent process dies:** Platform detects via timeout (now configured).
  But no automatic retry — operator must manually trigger the next
  pipeline stage.
- **Scout hangs on external site:** Observed in production. WebFetch to
  certain sites hangs indefinitely. Fixed by timeout configuration, but
  the hung scout's signals are lost for that day.
- **Machine sleep/hibernate:** Kills Claude processes. No recovery
  mechanism — pipeline stalls until next scheduled run.

**Timeout coverage:**
- All 15 agents now have timeout limits (20-30 min).
- No timeout on individual WebFetch calls within scout instructions —
  a single slow site can consume the full 20-min agent timeout.

**Silent failures:**
- Scout completes with 0 signals: no alert, no log entry. Could mean
  "no news today" or "sources were all unreachable."
- Daily brief not produced: no notification. Operator must check
  manually.
- Signal scoring discards items silently — no periodic review of
  discarded signals for false negatives.

**Data integrity:**
- Signals are JSON files. No schema validation. A malformed signal file
  could break downstream stages.
- Raw signals (32 files) and discarded signals (103 files) overlap — the
  OPS.md notes "raw/discarded overlap" as P1 issue.
- No checksums or integrity verification on signal files.

**System-level failure modes:**
- Primary machine goes down → no pipeline runs, no alerting.
- Database down → analytics queries fail, but signal pipeline continues
  (filesystem is source of truth). Good degradation.
- Claude subscription expires → all agents fail immediately. No
  graceful degradation, no fallback model.
- **Disaster recovery:** VPS migration guide is 80% complete but
  untested. Estimated recovery time: 2-4 hours if migration guide is
  followed. Longer if issues are discovered during migration.

---

## 4.6 Performance & Bottleneck Analysis

**Timing:**

| Pipeline Stage | Duration | Notes |
|---------------|----------|-------|
| 9 Scouts (parallel) | 2-13 min | Varies by source availability |
| Scout Lead | 7-15 min | Collects from all 9 scout directories |
| Senior Analyst | ~5 min | Scores signals by priority |
| Editor | ~5 min | Produces daily brief |
| **End-to-end** | **~30 min** | When all stages complete normally |

**Worst observed:** 936-minute (15.6 hour) runaway run on a single
scout. Root cause: no timeout configured at the time.

**Resource waste:**
- 15 backup files totaling 173MB. OPS.md flags "backup storage bloat"
  — no pruning policy.
- Server log at 170MB, unrotated. Growing indefinitely.
- Duplicate Pipeline Auditor agent consuming a slot.
- Signal files accumulate without cleanup — 470+ files across
  raw/scored/discarded/scouts, only growing.

**Cost analysis:**
- Claude subscription: fixed cost (Pro plan)
- Token usage: ~30 minutes of agent runtime/day across Sonnet 4.6
  (scouts, lead) and Opus 4.6 (analyst, editor) models
- VPS (planned): ~EUR 4/month for Hetzner CX22
- Headless Chrome for web-browsing scouts: CPU/memory overhead on
  local machine

---

## Phase 5: Security, Readiness & Recommendations

### 5.1 Security & Data Exposure

**Secrets:**
- Platform master key encrypts secrets at rest. Good.
- Claude CLI auth is shared across all agents (subscription-based).
  No per-agent authentication.
- Database credentials are hardcoded in OPS.md (`postgres://user:pass@...`).
  OPS.md is a local operations file, not in a public repo, but still
  poor practice.

**Network:**
- Platform server runs on localhost only (port 3100). Not exposed
  externally. Good.
- VPS migration guide correctly specifies: "Do NOT expose port 3100
  externally."
- Firewall rules in migration guide deny all incoming except SSH. Good.

**Supply chain:**
- Platform is a third-party agent orchestration tool (Paperclip).
  Dependency on their continued operation and updates.
- Claude CLI is the AI adapter — dependency on Anthropic's service
  availability.

### 5.2 Logging & Observability

- **Server log:** Single file, 170MB, unrotated. Contains platform
  events but not agent-level structured logs.
- **Run logs:** NDJSON per-run files (one per agent execution). Good
  granularity but no aggregation or search.
- **No monitoring dashboard.** Pipeline health is checked manually via
  the platform's web UI.
- **No alerting.** No email/Slack/webhook notification on failure.
- **No run-level metrics.** No tracking of "agent X took Y minutes" or
  "Z signals produced today" over time.

### 5.3 Documentation Quality

**Accuracy:**
- OPS.md is detailed and current (updated Apr 9 after the timeout
  incident). Agent timeout table matches the configured values.
- VPS-MIGRATION.md is 80% complete (draft status noted). Steps 1-9
  are detailed; step 10 (monitoring) is brief.
- PROJECT-MEMORY.md is stale — reports 12 agents when 16 exist.
  Listed as P1 known issue.

**Completeness:**
- OPS.md covers architecture, incident playbook, file locations, agent
  IDs, session history, and known issues. Excellent for an operations
  runbook.
- No user-facing README (this is a personal pipeline, not a shared
  tool). Acceptable.

**Onboarding:** Someone with Paperclip experience could operate this
system from OPS.md alone. The main gap is the stale PROJECT-MEMORY.md.

### 5.4 Goal Fulfillment

**Stated objective** (from OPS.md): Automated daily AI intelligence
pipeline that produces a brief covering 9 domains.

**Actual behavior:** The pipeline runs daily and produces briefs.
8 briefs produced in the last 11 days (gap during incident recovery).
333 scored signals, 103 discarded. The system works but has had one
major incident (9-hour stuck run).

**Verdict:** Goal 80% fulfilled. Core pipeline delivers. Reliability
gaps (no alerting, no auto-recovery) mean it requires periodic manual
supervision.

### 5.5 Blind Spots

| Blind Spot | Risk |
|-----------|------|
| No readership tracking | No evidence anyone reads the daily briefs. If nobody reads them, the entire pipeline is waste. |
| No signal quality feedback loop | Scored signals are never validated against ground truth. False positives/negatives accumulate. |
| No cost-per-brief tracking | Token consumption per run is not measured or tracked over time. |
| No pipeline success rate metric | No "X of last 30 days produced a brief" dashboard. |
| Discarded signal review is weekly | Potentially valuable signals sit in discard for up to 7 days before QA. |
| No source availability monitoring | If a scout's primary sources go down, it returns 0 signals — indistinguishable from "no news today." |

### 5.6 Objective Clarity Assessment

| Dimension | Rating (1-10) | Evidence |
|-----------|---------------|----------|
| Objective clarity | 9 | Clear: daily AI intelligence brief across 9 domains |
| Goal fulfillment | 7 | Produces briefs daily when running; 73% success rate over last 11 days |
| Delivery reliability | 5 | One 9-hour outage, no auto-recovery, no alerting |
| Output quality | 7 | Well-structured briefs; untested signal quality |
| Automation maturity | 7 | Fully automated daily run; lacks auto-recovery and monitoring |
| Self-improvement | 4 | Weekly auditor reports; no feedback from brief consumers |
| Operational visibility | 3 | Manual UI checking only; no dashboard, no metrics, no alerts |
| Resource efficiency | 5 | Backup/log bloat (343MB); no cleanup policy; duplicate agent |

### 5.7 Overall Rating

**5.5/10** — An ambitious multi-agent intelligence pipeline that delivers
on its core promise but lacks the operational maturity to run reliably
unattended. The architecture is sound (event-driven, clear agent
boundaries, file-based resilience), but the absence of monitoring,
alerting, automated tests, and log hygiene means failures are discovered
late and manually. The 9-hour stuck run — found by accident — is the
canonical example.

### 5.8 Production Readiness Assessment

| Gate | Status | Evidence |
|------|--------|----------|
| **Functionality** — does it do what it promises? | PARTIAL | Produces daily briefs across 9 domains. 73% daily success rate (8/11 days). |
| **Reliability** — consistent without manual intervention? | FAIL | 9-hour outage, no auto-recovery, pipeline requires periodic manual supervision. |
| **Error handling** — recovers gracefully? | PARTIAL | Timeouts now configured. But no auto-retry, no incident reporting, no fallback. |
| **Security** — no exposed secrets, injection, PII? | PARTIAL | Master key encryption, localhost-only server. But DB creds in OPS.md plaintext. |
| **Testing** — critical paths covered? | FAIL | Zero automated tests for a 16-agent autonomous system. |
| **Monitoring** — can you tell when something breaks? | FAIL | No alerting, no dashboard, no metrics. Manual UI checking only. |
| **Documentation** — can someone else operate this? | PASS | Excellent OPS.md runbook, detailed VPS migration guide. |
| **Scalability** — handles growth without redesign? | PARTIAL | 9 scouts near signal cap (36/day). Adding scouts is linear. Storage grows unbounded. |
| **Data integrity** — consistent, backed up, recoverable? | PARTIAL | Filesystem is source of truth (good). Backup bloat, raw/discarded overlap, no validation. |
| **Dependency health** — maintained, pinned, vulnerability-free? | PARTIAL | Pinned Paperclip version. Claude CLI managed externally. No dependency auditing. |

**Verdict:** Not production-ready. Needs monitoring/alerting, incident
auto-recovery, and basic tests before it can run truly unattended. The
core pipeline works, but operational maturity is not there yet.

### 5.9 Top 10 Ranked Recommendations

| # | Action | Impact | Effort | Who Implements |
|---|--------|--------|--------|----------------|
| 1 | Add alerting on pipeline failure (email/webhook when daily brief is not produced by 02:00 CET) | Critical | Medium | Human — configure notification agent or external monitor |
| 2 | Implement timeout incident reporting — auto-generate diagnostic report when agent times out | Critical | Medium | Human — extend Paperclip config or add wrapper script |
| 3 | Delete duplicate Pipeline Auditor agent | High | Low | Human — one API call |
| 4 | Add log rotation for server log (170MB and growing) | High | Low | Human — add logrotate config |
| 5 | Prune backup storage (173MB across 15 files) — keep last 3, delete rest | High | Low | Human — one-time cleanup + cron |
| 6 | Update PROJECT-MEMORY.md (says 12 agents, actual 16) | Medium | Low | Agent or human |
| 7 | Clean up raw/discarded signal overlap | Medium | Low | Human — audit and reconcile |
| 8 | Remove artifact files from project root (`2`, `5`, `8)`, `{assignee}`, etc.) | Low | Low | Human — delete 5 files |
| 9 | Add basic smoke test: trigger one scout, verify signal produced, verify brief produced | Medium | Medium | Human — write test script |
| 10 | Add per-run timing metrics (duration, signal count) to auditor's weekly report | Medium | Medium | Agent — extend auditor instructions |

### 5.10 The Uncomfortable Question

Is anyone reading the daily briefs? The pipeline produces intelligence
every weekday, but there's no feedback mechanism — no "useful/not useful"
signal, no read tracking, no engagement metric. If the briefs are
unread, this is an elaborate system that consumes a Claude subscription
and 30 minutes of compute daily to produce output nobody consumes. Before
investing in monitoring, tests, and VPS migration, the first question
is: does anyone actually use the output?

---

## Phase 6: Resilience Testing

**Backups:** 15 backup files totaling 173MB exist in the data directory.
No backup schedule documented. No restore procedure tested. The database
is explicitly described as "not the canonical data store" (filesystem
is source of truth), which reduces backup criticality — but the backup
files themselves are unmanaged bloat.

**Disaster recovery:** VPS migration guide (80% complete) is the closest
thing to a recovery plan. It covers full system migration but hasn't
been tested. Estimated recovery time: 2-4 hours following the guide,
longer if unexpected issues arise.

**Operational resilience:** The system runs on a single local machine.
If the machine is unavailable (power outage, hardware failure, OS
update), the pipeline stops with no failover. The VPS migration will
improve this but is not yet executed.

---

*Generated by [deep-project-audit](https://github.com/belousov-petr/deep-project-audit) v1.0.0*
