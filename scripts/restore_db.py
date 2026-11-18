#!/usr/bin/env python3
"""
AASHIMA ERP - Automated Database Restore Script
Restores database from compressed gzip backup archive.
"""

import os
import sys
import gzip
import shutil
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings

def run_restore(archive_path: Path):
    if not archive_path.exists():
        print(f"[Restore Error] Backup archive not found: {archive_path}")
        sys.exit(1)

    print(f"[Restore] Restoring from archive {archive_path}...")
    
    if settings.DATABASE_URL.startswith("sqlite"):
        db_file = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
        temp_dest = db_file.with_suffix(".tmp")
        with gzip.open(archive_path, 'rb') as f_in:
            with open(temp_dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        shutil.move(temp_dest, db_file)
        print(f"[Restore Success] SQLite database restored to: {db_file}")
    else:
        # PostgreSQL restore
        cmd = f"gunzip -c {archive_path} | psql -h {settings.POSTGRES_SERVER} -U {settings.POSTGRES_USER} -d {settings.POSTGRES_DB}"
        ret = os.system(cmd)
        if ret == 0:
            print(f"[Restore Success] PostgreSQL database successfully restored.")
        else:
            print(f"[Restore Error] psql restore failed with exit code: {ret}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore AASHIMA ERP database from gzip backup.")
    parser.add_argument("--file", required=True, help="Path to .gz backup archive")
    args = parser.parse_args()
    run_restore(Path(args.file))
