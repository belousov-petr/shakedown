# Resilience Testing - Reference

Detailed guidance for Phase 6. The goal is to verify that safety nets
work, not just that they exist. Test the system, don't admire it.

**Scope boundary:** This file covers hands-on testing (does recovery
*actually* work). For code-level failure mode analysis, see
`error-resilience.md` (Section 4.5). For live data store queries,
see `db-diagnostics.md` (Phase 3).

**Safety:** Every command in this file targets a TEMPORARY location
(`/tmp/`, throwaway database, separate file). Never restore over the
production target. Never run `DROP DATABASE` against anything you don't
own outright. If the project has only one copy of its data, stop and
ask before testing.

---

## 6a. Backup Discovery

Before testing, find what exists.

```bash
# Common backup locations - run from project root
find . -maxdepth 5 -type f \( \
  -name "*.sql" -o -name "*.sql.gz" -o -name "*.sql.bz2" \
  -o -name "*.dump" -o -name "*.bak" -o -name "*.backup" \
  -o -name "*.tar.gz" -o -name "*.tar.zst" \
  -o -name "*.sqlite" -o -name "*.sqlite3" -o -name "*.db" \
  -o -name "*.parquet" -o -name "*.csv.gz" \
\) 2>/dev/null | head -50

# Check standard backup directories
ls -lah ./backups/ ./backup/ ./dumps/ ./snapshots/ 2>/dev/null

# Check for cloud-backup configs (S3, GCS, Backblaze, restic, borg)
grep -rEl "s3://|gs://|b2://|restic|borg(matic)?|duplicity|rclone" \
  --include="*.yml" --include="*.yaml" --include="*.json" \
  --include="*.toml" --include="*.sh" . 2>/dev/null | head -10

# Check cron / systemd timers for scheduled backups
crontab -l 2>/dev/null | grep -iE "backup|dump|snapshot"
systemctl list-timers --all 2>/dev/null | grep -iE "backup|dump"
```

**Report**: backup count, latest timestamp, total size, oldest backup,
storage location (local / remote / both).

---

## 6b. Backup Structure Validation

Confirm files are not silently corrupt before attempting restore.

### PostgreSQL (`pg_dump`)

```bash
BACKUP=path/to/dump.sql.gz

# Plain SQL dump - check headers + uncompress integrity
gzip -t "$BACKUP" && echo "gzip OK"
zcat "$BACKUP" | head -20      # expect: -- PostgreSQL database dump
zcat "$BACKUP" | tail -5       # expect: -- PostgreSQL database dump complete

# Custom-format dump (.dump) - use pg_restore --list
pg_restore --list path/to/db.dump | head -30
pg_restore --list path/to/db.dump | wc -l   # entry count
```

### MySQL / MariaDB (`mysqldump`)

```bash
BACKUP=path/to/dump.sql.gz

gzip -t "$BACKUP" && echo "gzip OK"
zcat "$BACKUP" | head -10      # expect: -- MySQL dump
zcat "$BACKUP" | grep -c "INSERT INTO"     # row insertion count
zcat "$BACKUP" | tail -3       # expect: -- Dump completed on ...
```

### SQLite

```bash
DB=path/to/database.sqlite

# Quick integrity check - does NOT lock the file
sqlite3 "$DB" "PRAGMA integrity_check;"          # expect: ok
sqlite3 "$DB" "PRAGMA quick_check;"              # faster, less thorough
sqlite3 "$DB" "PRAGMA foreign_key_check;"        # FK violations
sqlite3 "$DB" ".schema" | head -30
sqlite3 "$DB" "SELECT name, COUNT(*) AS n FROM sqlite_schema GROUP BY type;"
```

### MongoDB

```bash
ARCHIVE=path/to/dump.archive.gz

# bsondump fails on truncated/corrupt archives
bsondump --type=json "$ARCHIVE" 2>&1 | tail -20
```

### Tar / Zstd archives

```bash
tar -tzf snapshot.tar.gz > /dev/null && echo "tar OK"
zstd -t snapshot.tar.zst && echo "zstd OK"
```

### Checksum verification

If the backup pipeline produces sidecar checksums (`.sha256`, `.md5`),
verify them. Mismatch means the backup is unusable even if it looks
intact.

```bash
sha256sum -c backup.sql.gz.sha256
```

**Red flag**: backups exist but no checksum sidecars and no
`pg_restore --list`-style validation. The team is hoping, not testing.

---

## 6c. Restore Test (the actual test)

Restore into a throwaway target and prove the data round-trips.

### PostgreSQL

```bash
# 1. Create a throwaway database (on the same instance, NOT prod)
createdb shakedown_restore_test

# 2. Restore
gunzip -c backup.sql.gz | psql -d shakedown_restore_test
# OR for custom format:
pg_restore -d shakedown_restore_test --no-owner --no-privileges backup.dump

# 3. Compare row counts against the source
psql -d production_db -tAc "SELECT
  schemaname, relname, n_live_tup
  FROM pg_stat_user_tables
  ORDER BY relname;" > /tmp/prod_counts.txt

psql -d shakedown_restore_test -tAc "SELECT
  schemaname, relname, n_live_tup
  FROM pg_stat_user_tables
  ORDER BY relname;" > /tmp/restored_counts.txt

diff /tmp/prod_counts.txt /tmp/restored_counts.txt
# Expect: no diff (or minor delta if backup was taken minutes ago)

# 4. Spot-check a critical table for row-level integrity
psql -d shakedown_restore_test -c "
  SELECT COUNT(*) AS rows,
         MIN(created_at) AS oldest,
         MAX(created_at) AS newest
  FROM users;"

# 5. Clean up
dropdb shakedown_restore_test
```

### SQLite

```bash
# 1. Copy the backup somewhere safe
cp backup.sqlite /tmp/restore_test.sqlite

# 2. Verify integrity
sqlite3 /tmp/restore_test.sqlite "PRAGMA integrity_check;"

# 3. Compare row counts to source for top N tables
for tbl in users orders events; do
  echo -n "$tbl: "
  echo -n "prod=$(sqlite3 production.sqlite "SELECT COUNT(*) FROM $tbl;") "
  echo "restore=$(sqlite3 /tmp/restore_test.sqlite "SELECT COUNT(*) FROM $tbl;")"
done

# 4. Clean up
rm /tmp/restore_test.sqlite
```

### MongoDB

```bash
# 1. Restore to a throwaway database
mongorestore --gzip --archive=dump.archive.gz \
  --nsFrom='production.*' --nsTo='shakedown_test.*'

# 2. Compare collection counts
mongosh --quiet --eval "
  db.getSiblingDB('production').getCollectionNames().forEach(c => {
    const p = db.getSiblingDB('production')[c].countDocuments();
    const r = db.getSiblingDB('shakedown_test')[c].countDocuments();
    print(c + ': prod=' + p + ' restore=' + r + (p===r ? ' OK' : ' MISMATCH'));
  });
"

# 3. Clean up
mongosh --quiet --eval "db.getSiblingDB('shakedown_test').dropDatabase();"
```

### File-based backups (logs, configs, generated artifacts)

```bash
# 1. Extract to /tmp
mkdir -p /tmp/restore_test && tar -xzf snapshot.tar.gz -C /tmp/restore_test

# 2. Compare file counts and sizes
find /path/to/source -type f | wc -l
find /tmp/restore_test -type f | wc -l

# 3. Compare a tree of checksums
( cd /path/to/source && find . -type f -exec sha256sum {} \; | sort ) > /tmp/src.sums
( cd /tmp/restore_test && find . -type f -exec sha256sum {} \; | sort ) > /tmp/rst.sums
diff /tmp/src.sums /tmp/rst.sums | head

# 4. Clean up
rm -rf /tmp/restore_test
```

**Report**: did the restore complete without errors? Did row/file
counts match? Did integrity checks pass? How long did it take?

---

## 6d. Recovery Time Objective (RTO) Measurement

Time the restore. Compare to the documented RTO. If undocumented, that
itself is the finding.

```bash
time gunzip -c backup.sql.gz | psql -d shakedown_restore_test
# real    7m23.412s
```

**Cross-check**: an undocumented or untested RTO means the team has no
basis for promising recovery to anyone else (customers, auditors,
incident response).

---

## 6e. Operational Resilience Checks

Beyond backups - can the system survive the things that actually break?

| Check | How |
|---|---|
| Documented recovery procedure exists | `find . -iname "RUNBOOK*" -o -iname "DR*" -o -iname "DISASTER*" -o -iname "RECOVERY*"` |
| Recovery procedure was actually tested | Look for dates in the runbook, test logs in `tests/dr/`, post-mortem references |
| Migration to different host is possible | Are paths absolute or env-relative? Is the DB connection a hard-coded localhost? Are credentials machine-specific? |
| RTO documented | Search docs for "RTO", "recovery time", "downtime budget" |
| RPO documented | Search docs for "RPO", "data loss tolerance", "backup frequency" |
| Single point of failure | Does one host / API key / cron job take everything down? |
| Backup is monitored | Does someone get paged when a backup fails? Is there an alert on stale-backup age? |
| Backups are off-site | Local-only backups die with the host - check for S3/GCS/B2 mirroring |
| Restore test is automated | Is restore verification in CI, or is it "we'll test when we need it"? |

---

## 6f. Common Findings (Report Template)

| Finding | Verdict | Evidence |
|---|---|---|
| Backups exist | PASS / FAIL | location + count + latest timestamp |
| Backups are valid | PASS / FAIL | integrity check output |
| Restore was tested in this review | PASS / FAIL | restored row counts match source |
| RTO is documented | PASS / FAIL | doc reference or "not found" |
| RTO matches reality | PASS / FAIL / UNKNOWN | measured restore time vs documented |
| Backups are off-site | PASS / FAIL | remote storage config found |
| Restore test is automated | PASS / FAIL | CI evidence or absence |
| DR runbook exists | PASS / FAIL | file path or "not found" |

If any row is FAIL or UNKNOWN, surface it in Section 5.8 (Production
Readiness, Data integrity gate) with evidence.
