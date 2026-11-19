#!/usr/bin/env python3
"""Create consistent SQLite or PostgreSQL backups with a SHA-256 sidecar."""

import argparse
import gzip
import hashlib
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy.engine import make_url
from backend.app.core.config import settings

BACKUP_DIR = Path(__file__).resolve().parent.parent / "infrastructure" / "backups"


def sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_backup(output_dir: Path = BACKUP_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    database_url = make_url(settings.DATABASE_URL)

    if database_url.get_backend_name() == "sqlite":
        source_path = Path(database_url.database).resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"SQLite database does not exist: {source_path}")
        final_path = output_dir / f"aashima_sqlite_{timestamp}.db.gz"
        with tempfile.TemporaryDirectory(dir=output_dir) as work_dir:
            snapshot_path = Path(work_dir) / "snapshot.db"
            source = sqlite3.connect(source_path)
            snapshot = sqlite3.connect(snapshot_path)
            try:
                source.backup(snapshot)
                integrity = snapshot.execute("PRAGMA integrity_check").fetchone()[0]
                if integrity != "ok":
                    raise RuntimeError(f"SQLite snapshot integrity check failed: {integrity}")
            finally:
                snapshot.close()
                source.close()
            temp_archive = Path(work_dir) / "backup.db.gz"
            with snapshot_path.open("rb") as raw_input, gzip.open(temp_archive, "wb") as compressed:
                shutil.copyfileobj(raw_input, compressed)
            os.replace(temp_archive, final_path)
    else:
        final_path = output_dir / f"aashima_postgres_{timestamp}.dump"
        fd, temp_name = tempfile.mkstemp(prefix=".aashima-backup-", dir=output_dir)
        try:
            with os.fdopen(fd, "wb") as output:
                environment = os.environ.copy()
                environment["PGPASSWORD"] = settings.POSTGRES_PASSWORD
                subprocess.run(
                    [
                        "pg_dump", "--format=custom", "--no-owner",
                        "--host", settings.POSTGRES_SERVER,
                        "--port", str(settings.POSTGRES_PORT),
                        "--username", settings.POSTGRES_USER,
                        "--dbname", settings.POSTGRES_DB,
                    ],
                    stdout=output,
                    check=True,
                    env=environment,
                )
            os.replace(temp_name, final_path)
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise

    digest = sha256_file(final_path)
    sidecar = final_path.with_suffix(final_path.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {final_path.name}\n", encoding="ascii")
    return final_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=BACKUP_DIR)
    arguments = parser.parse_args()
    try:
        result = run_backup(arguments.output_dir)
        print(f"Backup created and verified: {result}")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Backup failed: {error}", file=sys.stderr)
        sys.exit(1)
