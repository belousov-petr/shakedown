# Security: Traditional

> **Note**: Use this file for ALL projects. For LLM/agentic/governance content, see the sibling files.

# Security & Data Exposure - Reference

Detailed checks for Section 5.1. Run all that apply to the project.
Structured around traditional security plus OWASP GenAI frameworks.

### Foundational Architectural Principle

_[Ref: OWASP GenAI Data Security 2026, "What is Data Security in the
GenAI Context?" pp. 6-8]_

**The context window is a flat namespace with no internal access control.**
In GenAI systems, the context window aggregates data from multiple trust
domains - system prompts, user input, RAG results, tool outputs,
conversation history - into a single namespace where all inputs share
equal trust weight. The model cannot inherently distinguish trusted
instructions from untrusted data. This architectural fusion of control
and data planes is the root cause underlying most GenAI-specific risks
(DSGAI01, DSGAI11, DSGAI15, DSGAI19, DSGAI21). All mitigations in this
checklist work **around** this limitation rather than solving it.

**Core security posture**: GenAI systems must assume zero inherent trust
in the model (it can leak, regurgitate, or reconstruct data via
memorization, inversion, or output). Key principles:
- **Minimization**: only send what's needed; avoid over-broad context
- **Isolation**: per-tenant/per-user/per-agent boundaries; scoped tool
  permissions; HITL for high-risk/irreversible actions
- **Lifecycle rigor**: retention/erasure across raw + derived assets
  (embeddings, caches, backups, fine-tuned weights)
- **Integrity & provenance**: detect poisoning/tampering; track lineage
- **Continuous monitoring**: DLP on prompts/outputs/logs; anomaly
  detection for scraping/enumeration
- **Governance**: traceability, lawful basis, DSR support, audit readiness

---

## A. Traditional Application Security

### Secrets & Credentials

- Scan for hardcoded API keys, tokens, passwords, connection strings
- Check .gitignore - are .env, credentials, key files excluded?
- Check git history for accidentally committed secrets
- Are secrets in plaintext or encrypted/vault store?
- Are secrets stored in a vault and never exposed to LLMs?
  _[Ref: OWASP Secure MCP Server Development, Section 6]_

### Injection Vulnerabilities

- **SQL injection**: user input parameterized or string-concatenated?
- **Prompt injection**: can external data influence LLM system prompts?
  (see Section B for full LLM prompt injection analysis)
- **Command injection**: does any code pass user input to shell commands?
- **Path traversal**: can file paths be manipulated?
- **Code injection via MCP**: does the MCP server pass model-provided
  inputs directly into system commands, APIs, or DB queries without
  validation? _[Ref: OWASP Secure MCP Server Development, Vulnerability Landscape]_

### Privacy & PII

- Scan data files and database for PII (names, emails, phone numbers,
  addresses, IPs, financial data, government IDs)
- How is PII stored? Encrypted at rest? Access-controlled?
- Data retention policy? Are old records purged?
- GDPR: right to deletion, portability, consent tracking
- Are logs sanitized or do they contain sensitive data?
- Are prompts, context windows, and LLM outputs scanned for PII leakage?
  _[Ref: OWASP GenAI Data Security DSGAI01]_

### Supply Chain

- Dependencies from trusted sources? Lock files committed?
- Known CVEs? (`npm audit`, `pip audit`, `cargo audit`)
- CI/CD actions pinned to specific versions?
- AI Bill of Materials (AIBOM/SBOM): are AI components, model versions,
  and training data provenance inventoried?
  _[Ref: OWASP LLM Top 10 LLM03, Governance Checklist Section 3.3]_

### Workflow Security

- Who can trigger runs? Is there authentication?
- Can a worker escalate privileges or access other workers' data?
- Are webhook endpoints authenticated?

### Network & Infrastructure

- What ports are open? Localhost only or publicly accessible?
- TLS/SSL where needed?
- Rate limits on external services (LLM providers, APIs)
- Peak hour pricing or throttling

### Licensing & Legal Compliance

- What license does the project use? Is it appropriate for the use case?
- Are all dependency licenses compatible with the project license?
  (e.g., GPL dependency in an MIT project)
- Are there dependencies with restrictive or ambiguous licenses?
- Is license attribution present where required (NOTICE file, headers)?
- For data-handling projects: are there data processing agreements,
  terms of service compliance, or regulatory requirements (GDPR, CCPA)?
- For AI systems: are AI-specific legal risks addressed (IP ownership
  of AI-generated content, warranty implications, EULA review for
  GenAI platforms)? _[Ref: OWASP Governance Checklist Section 3.7]_

---
