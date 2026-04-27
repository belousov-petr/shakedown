# Performance & Bottleneck Analysis - Reference

Detailed checks for Section 4.6. Quantify everything possible.
Numbers beat narrative.

**Scope boundary:** This file covers measured/estimated performance
(timing, parallelism, scaling, cost). For structural scaling limits
(architecture, coupling, MECE), see `architecture-quality.md`
(Section 4.4). For storage waste specifically, see
`storage-efficiency.md` (Section 4.7).

---

## Timing

### End-to-end latency

```bash
# Wrap the entry point in `time`
time ./bin/run.sh         # OR: time python main.py
# real    2m14.612s
# user    1m42.310s
# sys     0m15.402s
```

If the entry point is a long-running service, use logs instead:

```bash
# Find the slowest N requests in the last 24h (structured JSON logs)
jq -r 'select(.duration_ms) | "\(.duration_ms) \(.endpoint)"' app.log \
  | sort -rn | head -20
```

### Stage-level breakdown (Python)

```bash
# Drop-in profiler for any script
python -m cProfile -o /tmp/run.prof main.py
python -m pstats /tmp/run.prof <<< "sort cumulative
stats 30"

# Or line-level (requires pip install line_profiler + @profile decorator)
kernprof -l -v main.py
```

### Stage-level breakdown (Node)

```bash
node --prof main.js                       # writes isolate-*.log
node --prof-process isolate-*.log | head  # human-readable
```

### Generic stage timing

If the project doesn't ship a profiler, look for/insert structured logs:

```python
import time
t0 = time.monotonic()
do_thing()
log.info("stage_done", stage="ingest", duration_ms=int((time.monotonic()-t0)*1000))
```

Then `jq` the logs as above.

---

## Parallelism

### What runs in parallel today

```bash
# Find existing parallelism patterns - threads, processes, async
grep -rEn "ThreadPoolExecutor|ProcessPoolExecutor|asyncio.gather|asyncio.create_task|multiprocessing|concurrent.futures|Promise.all|Promise.allSettled|spawn|worker_threads" \
  --include="*.py" --include="*.js" --include="*.ts" . | head -30

# Find serial loops that hit the network or DB - prime parallelization candidates
grep -rEn "for .* in .*:.*$" --include="*.py" -A 3 . \
  | grep -E "requests\.|httpx\.|fetch\(|cursor\.execute" | head -20
```

### Lock contention / race risk

```bash
grep -rEn "Lock\(\)|RLock\(\)|Semaphore|asyncio\.Lock|sync\.Mutex|threading\.Lock" \
  --include="*.py" --include="*.js" --include="*.ts" . | head
```

A single global lock around hot work caps throughput at 1; flag it.

---

## Scaling (Quantitative)

### What happens at 2x, 10x, 100x

For each major data store / queue / external API:

```bash
# Current row counts (pick relevant tables)
psql -tAc "SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 10;"

# Current storage size
psql -tAc "SELECT pg_size_pretty(pg_database_size(current_database()));"
psql -tAc "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;"

# SQLite equivalent
sqlite3 db.sqlite "SELECT name, SUM(pgsize) FROM dbstat GROUP BY name ORDER BY SUM(pgsize) DESC LIMIT 10;"
```

Then estimate: at current growth rate, when does the system hit its
scaling limit (free disk, query latency budget, monthly cost cap)?

### O(n^2) hunting

```bash
# Nested loops in the same scope - a starting point, not a guarantee
grep -rEn "for .* in .*:" --include="*.py" -A 5 . \
  | grep -B 1 "    for .* in .*:" | head -40

# Loop with database lookup (N+1 pattern - very common)
grep -rEn "for .* in .*:" --include="*.py" -A 3 . \
  | grep -B 1 "\.execute\(\|\.query\(\|\.get\(" | head -20
```

### Storage growth

```bash
# Track DB / log / data dir size over time if previous snapshots exist
du -sh data/ logs/ backups/ 2>/dev/null

# Total repo size (for skills/configs - bloat indicator)
git count-objects -vH 2>/dev/null
```

---

## Resource Waste (Quantified)

| Class | How to find | Report |
|---|---|---|
| Duplicate processing | `grep -rE "process_|run_|handle_" -l` then trace which stages overlap | "stages X and Y both compute Z; pick one" |
| Empty/low-value items | `find data/ -size 0`; row counts of `WHERE field IS NULL OR field = ''` | "37% of rows have no payload" |
| Redundant I/O | `strace -c -e trace=open,read,write ./bin/run.sh 2>&1 \| tail -20` | "same config file opened 14 times per run" |
| Oversized logs | `du -sh logs/*` and `ls -lhS logs/ \| head` | "app.log is 4.2 GB; rotation broken" |
| Token/API waste | grep for `client.chat.completions.create` / `messages.create` calls in loops; check for cache headers | "7 LLM calls per request, no prompt caching" |
| Polling that should be event-driven | grep for `while True:.*sleep`, `setInterval`, cron firing every minute | "heartbeat polls every 30s; switch to webhook" |

---

## Cost Analysis

Concrete cost calculations beat hand-waving.

### LLM cost (Anthropic / OpenAI / similar)

```python
# Pull token usage from logs/telemetry
# Example back-of-envelope for Claude Sonnet 4.6:
#   input  $3.00 per 1M tokens
#   output $15.00 per 1M tokens
#   cached input $0.30 per 1M tokens (90% discount)

# If 1000 calls/day, avg 8000 input + 2000 output tokens, no caching:
# input:  1000 * 8000 / 1e6 * $3   = $24/day
# output: 1000 * 2000 / 1e6 * $15  = $30/day
# total:  $54/day = ~$1620/month

# With prompt caching (95% cache hit on a 6000-token system prompt):
# cached: 1000 * 6000 * 0.95 / 1e6 * $0.30 = $1.71/day
# fresh:  1000 * 2000 / 1e6 * $3           = $6/day
# output: 1000 * 2000 / 1e6 * $15          = $30/day
# total:  ~$38/day = ~$1140/month  (-30%)
```

Always check whether prompt caching is wired in - it's the single
highest-leverage LLM optimization.

### External API cost

```bash
# Find every paid-API client init in the codebase
grep -rEn "openai\.|anthropic\.|stripe\.|twilio\.|sendgrid\.|apify_client\.|firecrawl|exa_py" \
  --include="*.py" --include="*.js" --include="*.ts" . | head -30

# Then: count calls per day from logs, multiply by per-call price
```

### Infrastructure cost

```bash
# Cloud provider tags / config (AWS / GCP / Azure)
grep -rEn "instance_type|machine_type|t2\.|t3\.|n1-|n2-|d2s_v3" \
  --include="*.tf" --include="*.yml" --include="*.yaml" --include="*.json" . | head
```

Multiply hourly rate * 24 * 30 for monthly compute cost.

### Subscription budgets

If the project rides on a paid plan (Apify, OpenRouter, Anthropic
console, GitHub Actions minutes), check budget headroom:

- Apify: dataset/storage/compute units consumed vs plan cap
- OpenRouter: monthly spend vs limit
- GH Actions: minutes used vs free tier (2000/mo for private)

---

## Optimization Opportunities

Surface every opportunity with measurable expected impact:

| Opportunity | Where | Expected impact |
|---|---|---|
| Add prompt caching | `src/llm.py:42` | -30% LLM cost |
| Batch DB writes | `src/ingest.py:88-94` (loop with .execute) | -80% write latency |
| Parallelize independent stages | `pipeline.py:120-160` | -45% wall time |
| Add covering index | `users.email` (WHERE used 14x/req) | -90% query latency |
| Replace cron polling with webhook | `crontab` line 3 | -100% polling cost |
| Compress hot logs | `logs/app.log` (4.2 GB plain text) | -85% disk |
| Cache external API responses | `src/maps.py:55` | -70% API spend |

For each row, the agent should be able to translate it into a
recommendation in Section 5.9 with the same impact estimate.
