# Security: Governance & Red Teaming

> **Note**: Use this file when the project must comply with AI governance frameworks (EU AI Act, NIST AI RMF, ISO 42001) or undergo formal red-teaming review. Otherwise skip.

## F. AI Governance & Compliance

**Applies to any project deploying AI in organizational settings.**
If pure non-AI project, note "No AI governance requirements - section skipped."

_[Ref: OWASP LLM Applications Cybersecurity and Governance Checklist v1.1,
genai.owasp.org/resource/llm-applications-cybersecurity-and-governance-checklist-english;
OWASP LLM & GenAI Security Center of Excellence Guide v1.0,
genai.owasp.org/resource/llm-and-generative-ai-security-center-of-excellence-guide]_

### AI Asset Inventory
- Are all AI services, tools, models, and owners cataloged?
- Is there an AI-specific tag in asset management?
- Are AI data sources cataloged with sensitivity classification?
- Is there an AI solution onboarding process?

### Threat Modeling for AI
- Has threat modeling been conducted for AI components?
- Are trust boundaries identified between AI and non-AI components?
- Are hyper-personalized attack scenarios considered (LLM-assisted
  spear phishing, deepfakes)?
- Is insider threat mitigation addressed for AI systems?

### AI-Specific Regulatory Compliance
- Are country/state AI compliance requirements identified?
- Is the project compliant with EU AI Act risk categories?
- Are AI tools used in hiring/employee management compliant with
  fairness requirements?
- Is the vendor's compliance with AI laws documented?

### Testing, Evaluation, Verification & Validation (TEVV)
- Is there a structured TEVV process for AI components?
- Are model performance metrics tracked over time?
- Is there regression testing for model behavior changes?
- Are model cards or risk cards maintained?

---

## G. Red Teaming & Adversarial Testing Readiness

**Applies to any project deploying AI in production.**
If no AI in production, note "No AI production deployment - section skipped."

_[Ref: OWASP GenAI Red Teaming Guide v1.0,
genai.owasp.org/2025/01/22/announcing-the-owasp-gen-ai-red-teaming-guide]_

### Red Teaming Process
- Has the project undergone GenAI-specific red teaming?
- Does red teaming cover model evaluation (bias, robustness, alignment)?
- Does red teaming cover implementation testing (guardrails, RAG security)?
- Does red teaming cover system evaluation (infrastructure, supply chain)?
- Does red teaming cover runtime analysis (human interaction, agent behavior)?

### Adversarial Testing Coverage
- Are prompt injection attacks tested (direct, indirect, multimodal)?
- Are guardrail bypass techniques tested?
- Are data exfiltration scenarios tested?
- Are hallucination/misinformation scenarios assessed?
- Are tool/plugin abuse scenarios tested?
- Are multi-agent attack chains assessed?

### Measurement Criteria & Success Thresholds
_[Ref: Red Teaming Guide Sections 7-8]_

- Are evaluation criteria non-binary? (LLM outputs are probabilistic - 
  a single success/failure is insufficient. Define statistical thresholds.)
- Is repeat prompting used? (Same prompt tested multiple times to account
  for non-determinism. If a prompt succeeds after N attempts, flag as
  vulnerable.)
- Is prompt brittleness tested? (Slight perturbations to prompts to
  evaluate consistency - same intent, different wording.)
- Are success/failure rates tracked per adversarial prompt to feed into
  future testing iterations?
- Are metrics tracked: vulnerability discovery rate, time to detection,
  coverage metrics, false positive rate, remediation effectiveness?
- Is severity classification defined? (Critical: immediate safety/security
  risk; High: significant ethical/operational impact; Medium: notable
  concern; Low: minor issue for tracking)

### What to Avoid in Red Teaming
_[Ref: Red Teaming Guide Section 9 - Best Practices]_

- Do NOT rely entirely on AI for security decision-making (complement,
  not replace, human judgment)
- Do NOT use real user data without proper consent and anonymization
- Do NOT underestimate the importance of securing training data
- Do NOT skip API security testing (most GenAI endpoints are APIs)
- Do NOT conduct one-time red teaming - model drift means continuous
  testing is required
- Do NOT overlook low-resource language bypass (AI safeguards can be
  tricked by translating unsafe inputs into low-resource languages)
- Do NOT ignore monitoring gaps - if prompt injection attempts occur
  without triggering alerts, that IS a critical finding

### Continuous Monitoring Requirements
_[Ref: Red Teaming Guide Appendix C; OWASP Governance Checklist]_

- Is there continuous monitoring of: response quality degradation,
  latency variations, resource bottlenecks (GPU/CPU/memory)?
- Is token usage monitored? (Jailbreak attempts often use high token counts)
- Is user activity monitored? (Activity peaks or extended sessions may
  indicate DDoS, prompt injection, or data extraction)
- Are prompts with low-resource languages detected and flagged?
- Is there automatic prompt tagging for categorization and tracking?
- Is user analytics and clustering used to find abnormal interactions?
- Is semantic consistency tracked? (Variance in responses to similar
  prompts across sessions - detect drift or inconsistencies)

### Red Team Tooling & Reporting
- Are automated adversarial testing tools used? Recommended tools:
  _[Ref: Red Teaming Guide Appendix B]_
 - **Garak** (NVIDIA) - generative AI red-teaming & assessment kit
 - **PyRIT** (Microsoft) - Python Risk Identification Toolkit
 - **Promptfoo** - LLM red teaming, pen testing, vulnerability scanning
 - **CyberSecEval** (Meta) - LLM security risk benchmarking
 - **HarmBench** - automated red teaming and robust refusal evaluation
 - **Invariant MCP-Scan** - MCP server security scanning
 - **Modelscan** (ProtectAI) - model serialization attack detection
 - **Giskard** - ML model and LLM test suites
 - **LlamaFirewall** (Meta) - agentic LLM risk scanners
 - **Llamator** - RAG application pentesting
- Is there structured reporting with severity classification?
- Are findings tracked to resolution?
- Is there periodic re-testing (not one-time)?
- Are Red Team findings integrated with production monitoring? (If
  adversarial tests succeed but production monitoring doesn't alert,
  that's a critical gap)
- Additional tools from Red Teaming Guide Appendix B:
 - **GOAT** (Meta) - automated agentic red teaming with adversarial prompts
 - **DeepEval** - LLM evaluation with multiple output metrics
 - **Foolbox** - adversarial attack benchmarking (PyTorch, TensorFlow, JAX)
 - **CleverHans** - ML vulnerability to adversarial examples
 - **HouYi** - automated prompt injection into LLM-integrated apps
 - **JailbreakingLLMs (PAIR)** - automated iterative jailbreak refinement
 - **LLM Attacks** - automatic adversarial attack construction
 - **LLM Canary** - benchmarking and scoring mechanisms
 - **PromptInject** - quantitative robustness analysis
 - **ps-fuzz** - interactive GenAI system prompt security assessment
 - **SplxAI** - automated continuous red teaming for conversational AI
 - **StrongREJECT** - jailbreak benchmark with evaluation methodology
 - **Dioptra** (NIST) - AI trustworthiness assessment platform
- Recommended datasets for adversarial testing:
 - **AdvBench** - adversarial attacks on aligned LLMs
 - **BBQ** - Bias Benchmark for QA
 - **HarmBench dataset** - standardized evaluation for robust refusal
 - **HAP** - Hate, Abuse, and Profanity detection
 - **Bot Adversarial Dialogue Dataset** (Meta)

### 12 Agentic Red Teaming Tasks
_[Ref: Red Teaming Guide Appendix D - Agentic AI Systems Red Teaming]_

For projects with agentic AI, the following 12 structured red teaming
tasks should be evaluated:

1. **Agent Authorization & Control Hijacking**: test unauthorized command
  execution, permission escalation, and role inheritance
2. **Checker-Out-of-the-Loop**: verify checkers are informed during
  unsafe operations; test fallback mechanisms
3. **Agent Critical System Interaction**: evaluate interactions with
  physical and critical digital systems; test fail-safe mechanisms
4. **Goal & Instruction Manipulation**: assess resilience against
  adversarial goal/instruction changes; test cascading goal manipulation
5. **Agent Hallucination Exploitation**: test vulnerability from
  fabricated outputs; evaluate validation mechanisms
6. **Agent Impact Chain & Blast Radius**: examine cascading failure
  risks; test inter-agent trust relationships and containment
7. **Agent Knowledge Base Poisoning**: inject malicious training data;
  test rollback capabilities
8. **Agent Memory & Context Manipulation**: simulate cross-session data
  leaks; test memory overflow and context manipulation
9. **Multi-Agent Exploitation**: intercept inter-agent communication;
  test trust relationships and coordination vulnerabilities
10. **Resource & Service Exhaustion**: simulate resource-intensive
  computations; exhaust API quotas; test fallback mechanisms
11. **Supply Chain & Dependency Attacks**: introduce tampered
  dependencies; test deployment pipeline security
12. **Agent Untraceability**: assess action traceability and forensic
  readiness; test logging suppression and data obfuscation

---
