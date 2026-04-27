# Security: LLM & GenAI

> **Note**: Use this file when the project uses LLM/GenAI components, vector stores, or MCP tools. For agentic-specific risks, see security-agentic.md.

## B. OWASP Top 10 for LLM Applications (2025)

**Applies to any project that uses, integrates, or deploys LLMs.**
If no LLM components detected, note "No LLM components - section skipped."

### LLM01: Prompt Injection
_[Ref: OWASP LLM Top 10 2025 - LLM01, genai.owasp.org/llmrisk/llm01-prompt-injection;
MITRE ATLAS: AML.T0051.000 (Direct), AML.T0051.001 (Indirect), AML.T0054 (Jailbreak)]_

- Can user input alter the LLM's behavior beyond intended scope?
- **Direct injection**: are there constraints on the model's role,
  capabilities, and limitations in the system prompt?
- **Indirect injection**: can external data sources (websites, files,
  tool outputs) influence LLM behavior?
- **Multimodal injection**: can hidden instructions in images, audio,
  or documents manipulate the model? (steganography, cross-modal attacks)
- **Jailbreaking** (distinct from prompt injection): can inputs cause
  the model to disregard safety protocols entirely?
- Is input/output filtering implemented? Semantic filters, string checks?
- Are expected output formats defined and validated deterministically?
- Is privilege control enforced (least privilege access for the LLM)?
- Is human approval required for high-risk actions?
- Is external content segregated and clearly identified as untrusted?
- Is adversarial testing (red teaming) conducted against prompt injection?
- Are low-resource language bypasses tested? (translating unsafe inputs
  into low-resource languages to evade safeguards)

### LLM02: Sensitive Information Disclosure
_[Ref: OWASP LLM Top 10 2025 - LLM02, genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure;
MITRE ATLAS: AML.T0024.000 (Infer Membership), AML.T0024.001 (Invert Model), AML.T0024.002 (Extract Model)]_

- Can the LLM leak PII, financial details, health records, or credentials
  through its output?
- Is data sanitization applied before user data enters training/fine-tuning?
- Are access controls enforced (least privilege) on data the LLM can access?
- Is the system prompt protected from extraction attempts?
- Are there Terms of Use policies allowing users to opt out of training?
- Is tokenization or redaction applied to sensitive content before processing?
- Is differential privacy or federated learning used where applicable?
- Is homomorphic encryption considered for privacy-preserving ML?
- Are model inversion attacks tested? _(ref: CVE-2019-20634 "Proof Pudding"
 - disclosed training data enabled model extraction and email filter bypass)_
- Is the system preamble concealed from user override attempts?
  _[Ref: OWASP API8:2023 Security Misconfiguration]_

### LLM03: Supply Chain Vulnerabilities
_[Ref: OWASP LLM Top 10 2025 - LLM03, genai.owasp.org/llmrisk/llm032025-supply-chain]_

- Are third-party models from trusted, verified sources?
- Are model versions pinned and integrity-verified (checksums/signatures)?
- Are pre-trained models scanned for backdoors or poisoned weights?
  (including ROME/lobotomization - direct model parameter manipulation)
- Are training data sources vetted for integrity and licensing?
- Is there an AI/ML SBOM using OWASP CycloneDX ML-BOM (ECMA-424 v1.7)?
- Are plugin/extension ecosystems audited for security?
- Are supply chain security gates integrated into CI/CD for AI components?
- **LoRA adapter risks**: are adapters verified before deployment?
  (malicious LoRA can compromise base model integrity; adapters from
  collaborative model merge environments need vetting)
- **On-device LLM risks**: are models encrypted with integrity checks?
  Is there vendor attestation for firmware? Can apps be reverse-engineered
  to extract/tamper with models?
- **Model merging risks**: are merged models re-evaluated for safety?
  (merged models can bypass published benchmark safety assurances)
- Are vendor T&Cs and data privacy policies reviewed? (unclear policies
  may expose sensitive data to model training)
- Is Data Version Control (DVC) or equivalent used to track dataset changes?

### LLM04: Data and Model Poisoning
_[Ref: OWASP LLM Top 10 2025 - LLM04, genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning;
MITRE ATLAS: AML.T0018 (Backdoor ML Model), AML.T0020 (Poison Training Data)]_

- Is training data validated for integrity, bias, and malicious content?
- Are data provenance and lineage tracked (CycloneDX ML-BOM)?
- Is there monitoring for data drift or anomalous training inputs?
- Are fine-tuning datasets reviewed for poisoning attempts?
- Are adversarial robustness tests run on the model?
- Is there a rollback mechanism for model versions?
- **Named attack techniques to test for**:
 - Split-View Data Poisoning (different data shown during validation vs training)
 - Frontrunning Poisoning (injecting data before legitimate collection)
 - Malicious pickling (model files executing arbitrary code on load)
 - Backdoor sleeper agents (hidden triggers activated by specific inputs)
  _[Ref: Anthropic research arXiv:2401.05566]_
 - Shadow Ray attack (Ray AI framework vulnerabilities exploited in the wild)
- Is Anthropic's finding noted? 250 poisoned samples (0.00016% of training
  tokens) produced measurable behavioral impact - the practical lower
  bound for effective poisoning is very low

### LLM05: Improper Output Handling
_[Ref: OWASP LLM Top 10 2025 - LLM05, genai.owasp.org/llmrisk/llm052025-improper-output-handling;
follow OWASP ASVS guidelines for input validation/sanitization]_

- Is LLM output treated as untrusted input by downstream components?
- Are outputs sanitized before rendering (preventing XSS, SSRF, code exec)?
- Are outputs validated against expected schemas or formats?
- Is there content filtering for harmful, toxic, or inappropriate content?
- Can LLM output trigger privileged operations without validation?
- Is context-aware output encoding applied (HTML, JavaScript, SQL, URL)?
- Are parameterized queries/prepared statements used for all DB operations?
- Is Content Security Policy (CSP) configured?
- Are path traversal vulnerabilities via LLM output prevented?
- Are CSRF protections applied to LLM-generated form submissions?
- Are email template phishing vectors considered (LLM generating malicious
  email content)?

### LLM06: Excessive Agency
_[Ref: OWASP LLM Top 10 2025 - LLM06, genai.owasp.org/llmrisk/llm062025-excessive-agency]_

- What functions/tools/plugins does the LLM have access to?
- Does the LLM have more permissions than necessary (violating least privilege)?
- Can the LLM perform destructive actions (delete, modify, send) without
  human approval?
- Are tool/function calls validated and constrained?
- Is there human-in-the-loop for high-risk actions?
- Are plugin permissions scoped to minimum necessary?
- Is there rate limiting on LLM-initiated actions?
- Are open-ended extensions avoided (shell commands, arbitrary URL fetching)?
- Are extensions executed in the user's context (OAuth with minimal scopes)?
- Is "complete mediation" applied? (downstream systems independently validate
  all requests, not trusting the LLM's authorization)
- Are SAST/DAST/IAST tools used to scan LLM input/output handling code?
- Is extension activity logged and monitored for anomalous patterns?

### LLM07: System Prompt Leakage
_[Ref: OWASP LLM Top 10 2025 - LLM07, genai.owasp.org/llmrisk/llm072025-system-prompt-leakage;
MITRE ATLAS: AML.T0051.000 (Meta Prompt Extraction)]_

- Can users extract the system prompt through direct queries?
- Does the system prompt contain sensitive information (API keys, internal
  URLs, business logic, confidential instructions)?
- Is the system prompt hardened against extraction techniques?
- Is prompt content separated from sensitive configuration?
- Are there guardrails preventing the LLM from revealing its instructions?
- **Critical**: security controls must be enforced independently of the
  system prompt - do NOT rely on "don't reveal X" instructions as a
  security mechanism. Delegate authorization to external systems.

### LLM08: Vector and Embedding Weaknesses
_[Ref: OWASP LLM Top 10 2025 - LLM08, genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses]_

- Are vector databases/embedding stores access-controlled?
- Is there per-tenant/per-user isolation in vector stores?
- Are embeddings encrypted at rest and in transit?
- Can adversarial inputs manipulate retrieval results?
- Are RAG retrieval results filtered based on user permissions (per-document ACLs)?
- Is there monitoring for unusual query patterns against vector stores?
- Is retrieved content validated before being injected into prompts?

### LLM09: Misinformation
_[Ref: OWASP LLM Top 10 2025 - LLM09, genai.owasp.org/llmrisk/llm092025-misinformation]_

- Are LLM outputs fact-checked or grounded in authoritative sources?
- Is RAG used to ground responses? Is the RAG pipeline secure?
- Are hallucinations/confabulations monitored and measured?
- Are there confidence scores or uncertainty indicators on outputs?
- Is there human review for high-stakes decisions based on LLM output?
- Are watermarking or provenance mechanisms used for AI-generated content?
- **Unsafe code generation**: does the LLM generate code that is
  reviewed for hidden backdoors or insecure patterns before use?
- Are field-of-use limitations clearly labeled in the UI?
- Are automatic validation mechanisms in place for high-stakes outputs?
- Is model fine-tuning or Parameter-Efficient Tuning (PET) used to
  reduce hallucination rates in domain-specific contexts?
- Are users educated on LLM limitations and encouraged to verify outputs?

### LLM10: Unbounded Consumption
_[Ref: OWASP LLM Top 10 2025 - LLM10, genai.owasp.org/llmrisk/llm102025-unbounded-consumption;
CWE-400 (Uncontrolled Resource Consumption)]_

- Are there rate limits on LLM API calls (per user, per session)?
- Are token/context window limits enforced?
- Is there budget monitoring and alerts for LLM API spend?
- Can a user trigger excessive resource consumption (DoS via large inputs)?
- Are there timeouts on LLM inference requests?
- Is there protection against model extraction (systematic API probing)?
- **Denial of Wallet (DoW)**: can an attacker cause excessive financial
  cost through crafted high-token or high-compute requests?
- **Continuous input overflow**: can inputs exceed the context window
  causing degraded/unpredictable behavior?
- **Resource-intensive queries**: are complex reasoning or large RAG
  retrieval operations bounded?
- **Side-channel attacks**: can model weights or architecture be inferred
  from timing, power consumption, or response patterns?
- Are logits/logprobs exposure limited or obfuscated?
- Are known glitch tokens filtered before context processing?
- Is watermarking implemented to detect unauthorized model copies?
- Is there a centralized ML model inventory/registry with governance?
- Are MLOps deployment workflows automated with security gates?

---

## D. MCP (Model Context Protocol) Security

**Applies to any project that develops, deploys, or consumes MCP servers.**
If no MCP components detected, note "No MCP components - section skipped."

_[Ref: OWASP Practical Guide for Secure MCP Server Development v1.0,
genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development;
OWASP Cheatsheet for Securely Using Third-Party MCP Servers v1.0,
genai.owasp.org/resource/cheatsheet-a-practical-guide-for-securely-using-third-party-mcp-servers-1-0]_

### MCP Architecture Security
- Local MCP: uses STDIO/Unix sockets? Bound to 127.0.0.1 if HTTP?
  If local HTTP, validate Origin header. Run in isolated/sandboxed
  subprocesses with minimal network access.
- Remote MCP: TLS 1.2+ enforced? JSON-RPC messages validated against
  MCP schema? Reject malformed/unrecognized data.
- Are MCP clients authenticated (OAuth 2.1/OIDC for remote)?
- Are users and sessions isolated (no shared global state)?
  No global variables, class-level attributes, or shared singletons
  for user-specific data. Use per-session objects or session-keyed stores.
- Is there deterministic session cleanup on termination/timeout?
  (all file handles, temp storage, in-memory contexts, cached tokens
  flushed and destroyed immediately)
- Are per-session resource quotas enforced (memory, CPU, rate limits)?
- Is network segmentation applied? (firewall rules or Kubernetes
  NetworkPolicies blocking all traffic except explicitly required)

### MCP Client Security _(consuming third-party MCP servers)_
_[Ref: OWASP Cheatsheet for Third-Party MCP Servers - Client Security]_
- **Trust minimization**: are all servers treated as untrusted? (validate
  manifests, enforce schemas, apply allowlists - never assume trustworthy)
- **Sandbox execution**: are clients run in containers (Docker) with
  limited filesystem/network access?
- **Just-in-Time (JIT) access**: are tool permissions temporary, narrowly
  scoped, with automatic expiration and instant revocation?
- **UI transparency**: are full tool descriptions, permissions, and data
  access exposed to users before execution? (no hidden/summarized views)
- **Local data protection**: is exfiltration of client-side secrets,
  history, or cached memory prevented?
- **Incident detection**: is there monitoring for unusual invocation
  patterns (mass file reads, excessive API calls)?

### MCP Server Discovery & Verification
_[Ref: OWASP Cheatsheet for Third-Party MCP Servers - Discovery]_
- **Registry-only discovery**: is a central registry maintained for all
  approved servers?
- **Origin verification**: are connections only to servers from trusted
  registries with IP allowlists and network isolation?
- **Version pinning**: is a manifest of approved server/tool versions
  maintained with checksums to prevent silent upgrades?
- **Staged rollout**: new servers deployed to staging with full telemetry
  first, promoted to production only after incident-free probation period?
- **Human approval recording**: are security and domain-owner approvals
  logged in the registry? Alert on drift from approved inventory.

### MCP Tool Safety
- Are tools cryptographically signed with version-pinned manifests?
- Is there a formal approval workflow for adding/updating tools?
  (code scanning SAST, dynamic testing, dependency scanning SCA,
  manual security review)
- Are tool descriptions validated against actual runtime behavior
  (detect tool poisoning)? Flag any tool performing actions not in
  its description (e.g., network writes not mentioned).
- Are only minimal necessary tool fields exposed to the model?
  (Tool Structure Validation - review all fields, keep internal metadata
  outside model context)
- Is there monitoring for "rug pull" attacks (tool description changes)?

### MCP Memory & Context Security
_[Ref: OWASP Cheatsheet for Third-Party MCP Servers - Memory Poisoning]_
- Is every memory update validated? (scan for anomalies, require source
  attribution, use cryptographic hashes)
- Is TTL enforced on stored data to prevent stale/malicious persistence?
- Is memory segmented per session/user to prevent cascading failures?
- Are agents prevented from writing to shared memory stores?

### MCP Tool Interference Prevention
_[Ref: OWASP Cheatsheet for Third-Party MCP Servers - Tool Interference]_
- When using multiple MCP servers, is there human-in-the-loop acceptance
  flow before executing tool actions? (tiered HITL for agentic systems)
- Is context isolated per tool execution (only necessary info passed)?
  Is LLM context reset between distinct executions?
- Are execution timeouts enforced to prevent looping/poorly implemented
  tools from impacting the host?

### MCP Data Validation
- Are all tool inputs/outputs schema-validated (JSON Schema)?
- Is input/output sanitized (XSS, SQL injection, RCE prevention)?
- Are size limits enforced on all tool outputs?
- Are resource usage quotas (rate limits, timeouts) per session?
- Is structured JSON tool invocation required (vs free-form text)?

### MCP Prompt Injection Controls
- Is human-in-the-loop required for high-risk tool actions?
  (using MCP elicitations for explicit confirmation)
- Is there an LLM-as-a-Judge approval check for high-risk actions?
  (dedicated approval check in a distinct context LLM session with
  policy prompt defining allowed/blocked tool calls)
- Are MCP sessions reset when switching contexts/tasks?
  ("One Task, One Session" - context compartmentalization prevents
  hidden instructions persisting in long conversation history)
- Are contexts compartmentalized to prevent instruction persistence?

### MCP Authentication & Authorization
- OAuth 2.1/OIDC enforced for all remote servers?
- Tokens short-lived, scoped, validated on every call?
  (validate iss, aud, exp, and signatures on every request)
- No token passthrough to downstream APIs? Use token delegation
  (RFC 8693) or On-Behalf-Of flows. Direct passthrough breaks review
  trails and creates Confused Deputy risk.
- Sessions not relied upon for identity (bound to validated credentials)?
- Policy enforcement centralized (dedicated gateway layer)?
- Client credentials for system operations; OIDC/PKCE for user operations?
- If OAuth cannot be implemented: narrowly scoped, short-lived
  Personal Access Tokens as alternative?
- Is Dynamic Client Registration protected? (require access tokens,
  Software Statements, or signed request bodies)
- Are least-permission OAuth scopes defined with granular per-identity
  action-level permissions?

### MCP Deployment & Governance
- Secrets in vault, never exposed to LLM?
- Server containerized, non-root, network-restricted?
- Supply chain controls: version-pinned deps, signed images, AIBOM?
- CI/CD security gates (fail on new vulnerabilities)?
  Use policy-as-code tools (e.g., OPA).
- Safe error handling (no stack traces, tokens, or paths in responses)?
- Audit logs for all tool invocations with parameter logging?
  (field-level allowlists, redaction/hashing to prevent sensitive data
  in verbose logs; store immutably for forensic analysis)
- Non-Human Identity governance (unique credentials per agent/service,
  continuously audit NHI systems for data access and tool usage)?
- Peer review required for new tools and major code changes?

### MCP Governance Workflow for Third-Party Servers
_[Ref: OWASP Cheatsheet for Third-Party MCP Servers - Governance]_
1. **Submission**: developer submits server with documentation + hash of
  tool descriptions
2. **Scanning**: automated security tools analyze for malware, hidden
  instructions, and risks
3. **Review & Sign-off**: security and domain experts review scan results;
  approved servers version-pinned and added to registry
4. **Deployment & Monitoring**: deployed to staging, monitored during
  probation period, then promoted to production
5. **Periodic Re-validation**: automatic re-scan at regular intervals
  or when versions change

**Recommended roles**: Submitter (Developer), Security Reviewer,
Domain Owner, Approver (both security + domain sign-off required),
Operator/SRE (manages rollout, monitoring, kill-switch)

### MCP Security Tools
_[Ref: OWASP Cheatsheet for Third-Party MCP Servers - Tools & Utilities]_
- **Invariant Labs MCP-Scan**: scans for malicious descriptions, prompt
  injections, tool poisoning, unsafe data flows
- **Semgrep MCP Scanner**: static analysis for Python/Node.js MCP deps,
  integrates with MCP-Get to scan listed servers
- **mcp-watch**: scans for insecure credentials storage and tool poisoning
- **Trail of Bits mcp-context-protector**: security wrapper for untrusted
  MCP servers
- **Vijil Evaluate**: AI agent evaluation for reliability, safety, security
- **LangKit**: LLM output monitoring toolkit
- **OpenAI Moderation API**: content detection
- **Invariant Labs Invariant**: contextual guardrails for agent systems
- **LlamaFirewall**: scanners for agentic LLM risks
- **OpenSSF Scorecard**: repository maturity verification
- **Snyk package health**: repository maintenance verification
- **Docker**: run MCP servers in containers for compute isolation

---

## E. GenAI Data Security Risks

**Applies to any project that processes, stores, or generates data using
GenAI systems.** If no GenAI data handling detected, note
"No GenAI data handling - section skipped."

_[Ref: OWASP GenAI Data Security Risks and Mitigations 2026 v1.0,
genai.owasp.org/resource/owasp-genai-data-security-risks-mitigations-2026]_

### Data Leakage (DSGAI01)
- Can the model or RAG system return sensitive data (PII/PHI/secrets/IP)
  through crafted prompts or high-recall queries?
- Are fine-tuned models/LoRA adapters tested for memorization of
  training data? (adapters memorize rare examples with higher fidelity)
- Are there output DLP controls (PII detectors, secret scanners)?
- Is markdown image rendering to external URLs blocked (exfiltration path)?
- Is cross-lingual leakage prevented? (regex controls useless if attacker
  asks for reply in another language, binary, or encoded text)
- Is "verifiable erasure / unlearning" addressed? Design model-aware
  deletion protocols (cryptographic erasure, machine unlearning) for
  high-risk cohorts so DSR erasure requests can be satisfied across raw
  data, embeddings, AND model checkpoints.
- Is policy-as-code used to enforce lawful basis, purpose limitation,
  and consent/approvals for training data ingestion?
- Is extraction/distillation defense active? Monitor API access for
  systematic probing, including reasoning trace coercion campaigns.
  _[Ref: Google Cloud Blog Feb 2026; Anthropic distillation detection]_
- Known CVEs: CVE-2024-5184 (EmailGPT), CVE-2025-54794 (Claude AI
  jailbreak), CVE-2025-32711 (M365 Copilot info disclosure),
  CVE-2026-22708 (Cursor terminal bypass), CVE-2026-0612 (Librarian
  info leak via web_fetch)

### Agent Identity & Credential Exposure (DSGAI02)
- Do agents inherit over-provisioned human OAuth tokens?
- Are agent credentials per-task, short-lived, and narrowly scoped?
- Is there NHI (Non-Human Identity) lifecycle governance?
- Can credentials propagate to sub-agents without re-scoping?
- Known CVE: CVE-2025-54795 (Claude Code confirmation prompt bypass
  for untrusted command execution)

### Shadow AI & Unsanctioned Data Flows (DSGAI03)
- Are there unapproved AI tools, browser plugins, or third-party LLM
  services in use?
- Is there an approved AI tool registry?
- Can data flow to unsanctioned AI services without detection?
- Are all five categories of Shadow AI monitored?
  1. Consumer/prosumer GenAI SaaS (ChatGPT, Copilot, Gemini)
  2. Third-party plugins with embedded AI (CRM plugins, email assistants)
  3. Startup/niche ML tools (domain-specific, potentially non-compliant regions)
  4. Internally built but ungoverned AI tooling
  5. AI features silently added to procured non-AI applications

### Data/Model/Artifact Poisoning (DSGAI04)
- Is training data integrity monitored (drift detection, golden sets)?
- Are datasets and model artifacts cryptographically signed?
- Is there an immutable model/artifact registry?
- Are human review gates in place for high-impact RAG corpora?
- Are inference-layer artifacts checked? (chat templates, loader configs,
  quantized formats like GGUF can embed covert behaviors without
  altering model weights)

### Data Integrity & Validation Failures (DSGAI05)
- Is ingestion validated (schema enforcement, content sanitization)?
  Validation at EVERY pipeline stage, not just initial upload.
- Are data transformations lossless where required?
- Is there consistency checking between source data and derived assets?

### Tool/Plugin/Agent Data Exchange Risks (DSGAI06)
- What data is shared between tools, plugins, and agents?
- Does each tool receive only minimal necessary context (not full transcript)?
- Are data exchange contracts defined and enforced?
- Is there a kill-switch to instantly disable any plugin/tool/agent?
- Are consequence-based authorization checks applied? (read-only with
  standard auth; reversible writes with logging; irreversible writes
  require human approval)
- Is trust transitivity controlled? (if A trusts B and B trusts C,
  compromising one boundary enables lateral movement across the graph)
- Known CVEs: CVE-2025-66404 (MCP Server/Kubernetes exec_in_pod abuse),
  CVE-2025-6514 (mcp-remote OS command injection via crafted auth endpoint)

### Data Governance & Lifecycle (DSGAI07)
- Are data classification labels propagated to derivatives (embeddings,
  caches, backups)?
- Is there end-to-end data lineage tracking using DBOM (Data Bill of
  Materials) format? Use CycloneDX ML-BOM (ECMA-424, v1.7) with RAG
  corpus version snapshots and embedding model version links.
- Are retention/erasure policies applied to all derived assets?
  Erasure must enumerate and act on ALL derived artifacts (embeddings,
  index entries, backups, training artifacts). Simulated deletion tests
  recommended: delete a test record, verify no trace in DB, logs,
  embeddings, backups, and model outputs.
- Is "no-train/no-retain" policy enforced for user uploads where applicable?
- Is TTL enforced on persistent agent context, cached retrievals, and
  agent memory?
- Are classification scanners at every pipeline ingress (re-classify at
  merge time, don't trust inherited labels)?

### Non-Compliance & Regulatory Violations (DSGAI08)
- Are DPIAs conducted before training/deploying models on personal data?
- Do DPIAs explicitly cover derived artifacts (embeddings, fine-tuned
  weights, retrieval indexes)?
- Is lawful basis documented for each dataset used in training?
- Is the erasure gap addressed? (deleting source records does NOT delete
  data from model weights, embeddings, or cached retrievals)
- Is data-to-model lineage maintained to enable targeted retraining
  when erasure obligations arise?
- Is there EU AI Act Article 10 readiness assessment for high-risk systems?
  (training data governance requirements effective August 2026)

### Multimodal Capture & Cross-Channel Leakage (DSGAI09)
- Are multimodal uploads (images, audio, video, documents) classified
  as high-sensitivity by default?
- Is OCR/ASR-based PII/secret detection applied to visual and audio inputs?
- Do derivatives (extracted text, transcripts, thumbnails) carry the
  same classification as the source media?
- Is training on user-provided multimodal content disabled by default?
- Are there short TTLs for transient multimodal storage?
- Is there red-teaming for cross-modal re-identification risks?
  (combining visual + audio + text traces to re-identify individuals)

### Synthetic Data & Anonymization Pitfalls (DSGAI10)
- Are synthetic and de-identified datasets treated as potentially
  personal by default (same classification as source)?
- Is re-identification risk formally measured before external sharing?
  (membership inference, quasi-identifier linkage)
- Is differential privacy applied for high-risk cohorts?
- Are quasi-identifier combinations suppressed or perturbed?
- Is there a Dataset Bill of Materials linking source to derived artifacts?
- Are transformation pipelines tested for encoding artifacts, schema
  drift, and Unicode handling issues?

### Cross-Context & Multi-User Conversation Bleed (DSGAI11)
- Are tenant IDs enforced at all layers (conversation store, vector DB,
  caches, prompt construction)?
- Are per-tenant or per-space retrieval indexes used (not just filters)?
- Are session IDs cryptographically bound to authenticated user identity?
- Is there automated testing for cross-tenant data bleed?
- Is KV-cache partitioned at the serving layer in multi-tenant deployments?
  _[Ref: NDSS 2025 - "Prompt Leakage via KV-Cache Sharing"]_
- Is fine-grained authorization (ABAC) applied at the retrieval layer?
- Is semantic response evaluation used to detect cross-context bleed
  that bypasses structural filters (paraphrased leakage)?
- Known CVE: CVE-2025-6515 (MCP SSE endpoint returns instance pointer
  as session ID - not unique or cryptographically secure)
- Known incident: ChatGPT March 2023 bug exposed users' conversation
  titles to others due to shared cache issues

### Unsafe NL Data Gateways / LLM-to-SQL (DSGAI12)
- Are LLMs restricted to stored procedures / parameterized templates
  (never arbitrary SQL against privileged connections)?
- Is row/column-level security enforced at the database layer regardless
  of how queries are produced?
- Are result-set size caps enforced (e.g., max 100 rows per NL query)?
- Are generated queries validated/linted before execution (schema
  constraints, deny-list of sensitive tables/columns, cost limits)?
- Is there anomaly detection on gateway access patterns?
- Is prompt injection hardening applied to query-generation context?
  (all content entering query generation treated as untrusted)
- Is forensic query attribution maintained? (durable, tamper-evident
  log linking every query to originating NL request, model intermediate
  representation, executing identity, and result metadata)
- Known CVEs: CVE-2024-8309 (LangChain GraphCypherQAChain prompt
  injection to malicious Cypher queries), CVE-2024-7042 (langchain-js
  prompt injection to SQL injection enabling multi-tenant breach)

### Vector Store Security (DSGAI13)
- Are vector stores encrypted at rest and in transit?
- Is tenant scoping enforced server-side?
- Are similarity query patterns monitored for extraction attempts?
- Is snapshot/import security controlled?

### Excessive Telemetry & Monitoring Leakage (DSGAI14)
- Do logs/traces capture full prompts or tool outputs (over-logging)?
- Are prompts, tool outputs, and secrets tokenized/redacted in logs?
- Are debug traces time-limited with approval workflows?
- Is access to observability platforms controlled and monitored?

### Over-Broad Context Windows (DSGAI15)
- Is context minimized (only necessary data sent to the model)?
- Are there controls preventing sensitive data from mixing with
  untrusted user input in the same context window?
- Is there per-segment access control within the context?
- Are prompt "shapers" or gateway middleware enforcing field-level
  redaction before calls to external LLM providers?
- Are prompt size limits enforced with justification for each data element?
- Is there detection of "field creep" (auto-context features silently
  expanding over time)?

### Endpoint & Browser Assistant Overreach (DSGAI16)
- Are AI browser extensions and local copilots on an enterprise allow-list?
- Are extension permissions minimized (no "read all sites", no full
  filesystem access)?
- Is there detection of HashJack-style attacks (prompt injection via
  URL fragments that bypass server-side controls)?
  _[Ref: TechRadar - "AI browsers can be hacked with a simple hashtag"]_
- Is local AI memory (browser history, sidebar stores) treated as
  sensitive data with classification, retention, and encryption?
- Are EDR/CASB/DLP controls tuned for AI extension exfiltration patterns?

### Data Availability & Resilience in AI Pipelines (DSGAI17)
- Is staleness signaling implemented? (RAG pipeline propagates index
  freshness metadata; silent failover to stale replicas prohibited)
- Are erasure operations propagated synchronously to all replicas
  and failover targets (DSR-aware replication)?
- Do backup/restore drills include semantic validation of AI artifacts
  (nearest-neighbor result consistency, model output regression)?
- Are RTO/RPO objectives defined for vector stores, embedding indices,
  and model registries as first-class infrastructure components?

### Inference & Data Reconstruction (DSGAI18)
- Are API confidence scores / logits / logprobs restricted or bounded?
- Are rate limits and query budgets enforced to prevent inference probing?
- Are embeddings protected with noise/quantization and restricted k-NN?
- Are membership inference audits conducted against deployed models?
- Are LoRA adapters audited for training data extractability?

### Human-in-the-Loop & Labeler Overexposure (DSGAI19)
- Are labelers given only minimal necessary data (identifiers redacted)?
- Are vendor security controls enforced (device controls, NDAs, monitoring)?
- Is synthetic/perturbed data used for labeling tasks where exact text
  is not required?
- Are audit trails maintained tying each sample to a specific reviewer?

### Model Exfiltration & IP Replication (DSGAI20)
- Are API access patterns monitored for systematic probing (model
  extraction campaigns)?
- Is watermarking implemented to detect unauthorized model copies?
- Are model download/export endpoints restricted to authorized consumers?

### Disinformation via Data Poisoning (DSGAI21)
- Can adversarial content planted in RAG retrieval pipelines influence
  model output in trusted contexts?
- Are retrieval sources validated and trust-scored?
- Is there monitoring for planted disinformation in knowledge bases?

---
