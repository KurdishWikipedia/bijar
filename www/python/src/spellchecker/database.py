# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Database Connection Manager
This module handles the setup and provision of database connections.
It automatically switches between local (.env) and Toolforge (replica.my.cnf)
configurations using the PyMySQL library.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Dict, Any, cast
from dotenv import load_dotenv
import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

load_dotenv()

# --- Configuration Switch based on FLASK_ENV ---
db_config: Dict[str, Any]
is_production = os.getenv('FLASK_ENV') == 'production'

if is_production:
    # --- Toolforge Production Config ---
    print("🚀 Running in production mode.")
    db_config = {
        "read_default_file": os.path.expanduser('~/replica.my.cnf'),
        "host": 'tools.db.svc.wikimedia.cloud',
        "database": os.getenv("DB_NAME"),
        "charset": 'utf8mb4',
        "cursorclass": DictCursor
    }
else:
    # --- Local Development Config ---
    print("💻 Running in local development mode.")
    db_config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "ckb_spellchecker_db"),
        "charset": 'utf8mb4',
        "cursorclass": DictCursor
    }

@contextmanager
def get_db_connection() -> Generator[Connection[DictCursor], None, None]:
    """Provides a PyMySQL database connection, ensuring it's closed."""
    # Use a string literal in 'cast' to satisfy the type checker without a runtime error.
    db_conn = cast("Connection[DictCursor]", pymysql.connect(**db_config))
    try:
        yield db_conn
    finally:
        if db_conn:
            db_conn.close()
