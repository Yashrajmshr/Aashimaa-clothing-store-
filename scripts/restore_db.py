#!/usr/bin/env python3
"""Restore a verified backup into a new, non-existing target only."""

import argparse
import gzip
import hashlib
import hmac
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy.engine import make_url
from backend.app.core.config import settings


def verify_checksum(archive: Path, allow_legacy: bool) -> None:
    checksum_file = archive.with_suffix(archive.suffix + ".sha256")
    if not checksum_file.is_file():
        if allow_legacy:
            return
        raise ValueError("Backup checksum is missing; use --allow-legacy-no-checksum only for a trusted legacy archive")
    checksum_parts = checksum_file.read_text(encoding="ascii").split()
    if not checksum_parts:
        raise ValueError("Backup checksum file is empty")
    expected = checksum_parts[0].lower()
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if not hmac.compare_digest(expected, digest.hexdigest()):
        raise ValueError("Backup checksum does not match")


def restore_sqlite(archive: Path, target: Path) -> Path:
    source_database = make_url(settings.DATABASE_URL).database
    target = target.resolve()
    if source_database and target == Path(source_database).resolve():
        raise ValueError("Restore target cannot be the configured source database")
    if target.exists():
        raise FileExistsError("Restore target already exists; restore never overwrites a database")
    target.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(prefix=".aashima-restore-", suffix=".db", dir=target.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with gzip.open(archive, "rb") as compressed, temp_path.open("wb") as output:
            shutil.copyfileobj(compressed, output)
        with temp_path.open("rb") as restored_file:
            if restored_file.read(16) != b"SQLite format 3\x00":
                raise ValueError("Archive does not contain a valid SQLite database")
        restored = sqlite3.connect(temp_path)
        try:
            result = restored.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise ValueError(f"Restored database integrity check failed: {result}")
        finally:
            restored.close()
        os.link(temp_path, target)
        return target
    finally:
        temp_path.unlink(missing_ok=True)


def restore_postgres(archive: Path, target_database: str) -> str:
    if not target_database or target_database == settings.POSTGRES_DB:
        raise ValueError("PostgreSQL restore requires a new target database name different from the configured database")
    environment = os.environ.copy()
    environment["PGPASSWORD"] = settings.POSTGRES_PASSWORD
    common = [
        "--host", settings.POSTGRES_SERVER,
        "--port", str(settings.POSTGRES_PORT),
        "--username", settings.POSTGRES_USER,
    ]
    subprocess.run(["createdb", *common, target_database], check=True, env=environment)
    if archive.name.endswith(".sql.gz"):
        with gzip.open(archive, "rb") as sql_stream:
            subprocess.run(
                ["psql", *common, "--dbname", target_database, "--set", "ON_ERROR_STOP=1"],
                stdin=sql_stream,
                check=True,
                env=environment,
            )
    else:
        subprocess.run(
            ["pg_restore", *common, "--no-owner", "--exit-on-error", "--dbname", target_database, str(archive)],
            check=True,
            env=environment,
        )
    return target_database


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path, help="Verified .db.gz or PostgreSQL .dump archive")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--target-file", type=Path, help="New SQLite file path; it must not already exist")
    target.add_argument("--target-database", help="New PostgreSQL database name; it must not already exist")
    parser.add_argument("--allow-legacy-no-checksum", action="store_true", help="Allow a trusted archive made before checksum sidecars existed")
    arguments = parser.parse_args()
    try:
        if not arguments.file.is_file():
            raise FileNotFoundError("Backup archive not found")
        verify_checksum(arguments.file, arguments.allow_legacy_no_checksum)
        if arguments.target_file:
            if not arguments.file.name.endswith(".db.gz"):
                raise ValueError("SQLite restore requires a .db.gz archive")
            result = restore_sqlite(arguments.file, arguments.target_file)
        else:
            if arguments.file.name.endswith(".db.gz"):
                raise ValueError("A SQLite archive requires --target-file")
            result = restore_postgres(arguments.file, arguments.target_database)
        print(f"Restore completed into new target: {result}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Restore failed: {error}", file=sys.stderr)
        sys.exit(1)
