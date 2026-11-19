# AASHIMA ERP Backup and Recovery Guide

**Status:** Safer local scripts are implemented and SQLite backup/restore is tested on disposable data. PostgreSQL execution, remote encryption/storage, retention, and a production recovery drill remain unverified.

## Script behavior

- `scripts/backup_db.py` uses SQLite's online backup API or PostgreSQL `pg_dump` custom format, then writes a SHA-256 sidecar.
- `scripts/restore_db.py` requires a new target. SQLite restore refuses an existing path and checks both the checksum and database integrity. PostgreSQL restore creates a new database with a name different from the configured active database; it never drops an existing database.
- Older archives without sidecars require the explicit `--allow-legacy-no-checksum` option and should only be used when their provenance is trusted.

Example for a new SQLite target:

```powershell
python scripts/backup_db.py
python scripts/restore_db.py --file infrastructure/backups/<archive>.db.gz --target-file D:/restore/aashima_recovered.db
```

For PostgreSQL, pass `--target-database` with a new, unused name. If a PostgreSQL restore fails after database creation, the script leaves that new target intact for operator review; it does not automatically drop it.

## Before production approval

1. Use database-native consistent backups: PostgreSQL `pg_dump` in custom format, or SQLite's online backup API while the application is quiesced.
2. Encrypt backups at rest and in transit. Store at least one copy outside the application host with separate access credentials.
3. Record backup time, database identity, schema migration revision, checksum, and completion status. Alert on backup failure.
4. Define and approve business recovery point (RPO) and recovery time (RTO) objectives.
5. Run a scheduled restore drill into an isolated environment. Verify schema, foreign keys, invoice PDFs/media references, and application read/write health.
6. Keep a pre-restore snapshot of the destination and document operator, approval, and cutover decision.

## Recovery outline

1. Declare an incident and stop writes or isolate the affected application.
2. Identify the last known-good, checksum-verified backup and the matching application/migration revision.
3. Restore into a new isolated database target. Never overwrite the only copy of the current database.
4. Apply only reviewed migrations, validate database integrity and key financial totals, and verify related media.
5. Have the business owner approve the recovery point and restored totals.
6. Point the application at the recovered target, run health and role/privacy checks, then resume traffic.
7. Preserve the incident database and logs for investigation; document the data-loss window and actions.

## Current limitations

- PostgreSQL commands use argument arrays and the configured password through the process environment; PostgreSQL execution was unavailable during this audit.
- The scripts do not encrypt off-host backups, implement retention, or provide restore of media files.
- No PostgreSQL instance or complete application recovery drill was available during this audit.

Do not use these scripts as the sole production backup/recovery mechanism until PostgreSQL restore, off-host encrypted storage, retention, and full application recovery are tested.
