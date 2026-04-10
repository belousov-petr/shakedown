# Architecture & Code Quality — Reference

Detailed checks for Section 4.4. Evaluate structure, patterns, and
quality — don't just list what exists.

---

## Structural Analysis

### Storage & Data Flow
- Storage model trade-offs: file vs DB, consistency, queryability
- Data flow tracing: can you follow data from input to output?
- Are intermediate representations necessary or redundant?
- Schema/contract inconsistencies between components
- State management: where does state live, who mutates it?

### Infrastructure Gaps
- Missing infrastructure: monitoring, alerting, retry, graceful degradation
- Single points of failure: what has no redundancy?
- Configuration management: hardcoded values vs externalized config
- Deployment: is there a repeatable deployment process?

### Scalability (Structural)

**Scope:** Architectural scaling limits — what *structurally* prevents
growth. For quantitative performance at scale (timing, cost), see
`performance-analysis.md` (Section 4.6).

- What breaks at 2x, 10x, 100x current load?
- Sequential bottlenecks and idle time
- Are there O(n^2) or worse operations hiding in loops?
- Unbounded data structures (lists that grow forever, queues with no cap)
- Can components scale independently or is everything coupled?

---

## Design Patterns & Coherence

### Pattern Consistency
- Are design patterns consistent across the codebase?
- Is there a clear architectural style (MVC, layered, event-driven, pipes)?
- Or is it ad-hoc — different patterns in different corners?

### MECE Analysis
Responsibilities should be **Mutually Exclusive** and **Collectively
Exhaustive**:
- **Overlapping ownership**: do two components/agents/modules handle the
  same concern? (e.g., both a middleware and a handler validate input)
- **Gaps**: is any concern unowned? (e.g., error reporting exists but
  nobody aggregates or alerts on it)
- **Boundary clarity**: are interfaces between components well-defined
  or do they reach into each other's internals?

### Contradictions
- Do any instructions, configs, or code paths contradict each other?
- Does the config say one thing but the code does another?
- Are there competing implementations of the same logic?
- Do agent/worker instructions reference files, functions, or APIs
  that don't exist?

---

## Algorithm & Logic Quality

### Efficiency
- Are algorithms appropriate for the data size? (e.g., linear search
  on a large dataset instead of hash lookup)
- Are there unnecessary nested loops or repeated computations?
- Is caching used where appropriate? Is it invalidated correctly?
- Are expensive operations (API calls, DB queries, file I/O) minimized?

### Logic Flow
- Can you trace the main execution path without getting lost?
- Are there unreachable code paths or dead branches?
- Is control flow clear or buried in callbacks/promises/event chains?
- Are there race conditions in concurrent code?

### Cyclomatic Complexity
- Are there functions with deeply nested conditionals (>3 levels)?
- Long functions (>50 lines) that should be decomposed?
- Switch/if-else chains that could be lookup tables or polymorphism?

---

## Code Quality

### File Organization
- Any files > 500 lines that should be split?
- Is the directory structure logical and navigable?
- Are related files colocated or scattered?

### Dead Code & Debt
- Dead code: functions never called, imports never used
- Commented-out blocks left "just in case"
- Unaddressed TODOs and FIXMEs — count them, assess severity
- Deprecated patterns still in use

### Naming & Consistency
- Naming consistency across the codebase (camelCase vs snake_case mixed?)
- Do names describe intent or implementation? (`processData` vs
  `enrichUserProfile`)
- Are abbreviations consistent or do they vary?

### Dependency Graph
- How tightly coupled are components?
- Are there circular dependencies?
- Could any component be extracted as an independent module?
- Are internal APIs stable or do they change with every feature?

---

## Test Coverage

### Test Existence
- Do tests exist? What kind (unit, integration, e2e, contract)?
- Where do they live? Are they colocated or in a separate tree?
- Can they be run with a single command?

### Coverage Assessment
- What's the estimated coverage? (tool output if available, manual
  assessment otherwise)
- Are **critical paths** tested? (payment flows, auth, data mutations,
  external integrations)
- Are **edge cases** tested? (empty input, max values, concurrent access)
- Are **failure paths** tested? (timeouts, invalid input, service down)

### Test Quality
- Do tests actually assert behavior or just confirm "no crash"?
- Are tests deterministic (no flaky tests dependent on timing/ordering)?
- Is test data realistic or trivial?
- If no tests: flag as critical gap for production readiness

---

## Output Correctness

Beyond "does it run without errors" — does it produce *right* results?

### Result Validation
- Can the output be verified against a known-good baseline?
- Are there sanity checks on output (expected ranges, formats, sizes)?
- Are there outputs that look plausible but are wrong? (hallucination,
  stale cache, wrong data source)

### Data Transformation Integrity
- If the system transforms data: is the transformation lossless where
  it should be? (counts in = counts out, sums preserved)
- Are there rounding, truncation, or encoding issues?
- Does the output schema match what downstream consumers expect?

### Determinism
- Given the same input, does the system produce the same output?
- If non-deterministic (LLM, random sampling): is the variance acceptable?
- Are there race conditions that affect output ordering or content?

### Output Freshness
- Is the output based on current data or stale cache?
- Are there timestamps indicating when the output was generated?
- Could a user mistake old output for current?
