#!/usr/bin/env python3
"""
AASHIMA ERP - Automated Database Backup Script
Dumps PostgreSQL or SQLite database to timestamped gzip archive.
"""

import os
import sys
import gzip
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings

BACKUP_DIR = Path(__file__).resolve().parent.parent / "infrastructure" / "backups"

def run_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    if settings.DATABASE_URL.startswith("sqlite"):
        db_file = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
        if not db_file.exists():
            print(f"[Backup Error] SQLite DB file not found: {db_file}")
            sys.exit(1)
        backup_file = BACKUP_DIR / f"aashima_sqlite_backup_{timestamp}.db.gz"
        print(f"[Backup] Compressing SQLite database {db_file} -> {backup_file}...")
        with open(db_file, 'rb') as f_in:
            with gzip.open(backup_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"[Backup Success] Saved archive to: {backup_file}")
    else:
        # PostgreSQL dump
        backup_file = BACKUP_DIR / f"aashima_postgres_backup_{timestamp}.sql.gz"
        print(f"[Backup] Triggering pg_dump for {settings.POSTGRES_DB}...")
        cmd = f"pg_dump -h {settings.POSTGRES_SERVER} -U {settings.POSTGRES_USER} -d {settings.POSTGRES_DB} | gzip > {backup_file}"
        ret = os.system(cmd)
        if ret == 0:
            print(f"[Backup Success] PostgreSQL archive saved to: {backup_file}")
        else:
            print(f"[Backup Error] pg_dump failed with exit code: {ret}")

if __name__ == "__main__":
    run_backup()
