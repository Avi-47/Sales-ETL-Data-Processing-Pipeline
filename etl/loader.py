"""
LOAD MODULE
-----------
Loads transformed sales data into a SQLite database.

Tables Created:
  - sales          : Clean, enriched sales records
  - rejected_sales : Records that failed validation
  - etl_audit_log  : Run-level ETL metadata
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ── SQL Statements ────────────────────────────────────────────────────────────

CREATE_SALES_TABLE = """
CREATE TABLE IF NOT EXISTS sales (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id         INTEGER NOT NULL UNIQUE,
    customer_name    TEXT    NOT NULL,
    customer_email   TEXT,
    product_name     TEXT    NOT NULL,
    category         TEXT,
    quantity         INTEGER NOT NULL,
    unit_price       REAL    NOT NULL,
    discount_percent REAL    DEFAULT 0,
    gross_amount     REAL,
    discount_amount  REAL,
    net_amount       REAL,
    region           TEXT,
    order_date       TEXT,
    status           TEXT,
    loaded_at        TEXT    DEFAULT (datetime('now'))
);
"""

CREATE_REJECTED_TABLE = """
CREATE TABLE IF NOT EXISTS rejected_sales (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id         TEXT,
    customer_name    TEXT,
    customer_email   TEXT,
    product_name     TEXT,
    category         TEXT,
    quantity         TEXT,
    unit_price       TEXT,
    discount_percent TEXT,
    region           TEXT,
    order_date       TEXT,
    status           TEXT,
    rejection_reason TEXT,
    rejected_at      TEXT DEFAULT (datetime('now'))
);
"""

CREATE_AUDIT_TABLE = """
CREATE TABLE IF NOT EXISTS etl_audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at          TEXT,
    source_file     TEXT,
    total_extracted INTEGER,
    total_loaded    INTEGER,
    total_rejected  INTEGER,
    status          TEXT
);
"""


def _create_tables(conn: sqlite3.Connection):
    """Create all required tables if they don't exist."""
    cursor = conn.cursor()
    cursor.executescript(
        CREATE_SALES_TABLE +
        CREATE_REJECTED_TABLE +
        CREATE_AUDIT_TABLE
    )
    conn.commit()
    logger.info("📋 Tables verified/created in SQLite.")


def load(
    clean_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
    db_path: str,
    source_file: str
) -> dict:
    """
    Load clean and rejected records into SQLite database.

    Args:
        clean_df    : Transformed, valid sales records.
        rejected_df : Records that failed validation.
        db_path     : Path to the SQLite database file.
        source_file : Source CSV path (for audit log).

    Returns:
        dict with run summary statistics.
    """
    logger.info(f"💾 Loading data into SQLite: {db_path}")

    conn = sqlite3.connect(db_path)

    try:
        _create_tables(conn)

        # ── Load clean records ────────────────────────────────────────────
        loaded_count = 0
        skipped_count = 0

        if not clean_df.empty:
            clean_cols = [
                "order_id", "customer_name", "customer_email",
                "product_name", "category", "quantity", "unit_price",
                "discount_percent", "gross_amount", "discount_amount",
                "net_amount", "region", "order_date", "status"
            ]
            # Only insert columns that exist in DataFrame
            available_cols = [c for c in clean_cols if c in clean_df.columns]
            insert_df = clean_df[available_cols]

            # Use INSERT OR IGNORE to skip duplicate order_ids
            cursor = conn.cursor()
            for _, row in insert_df.iterrows():
                try:
                    placeholders = ", ".join(["?"] * len(available_cols))
                    col_names    = ", ".join(available_cols)
                    sql = f"INSERT OR IGNORE INTO sales ({col_names}) VALUES ({placeholders})"
                    cursor.execute(sql, tuple(row))
                    if cursor.rowcount > 0:
                        loaded_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    logger.error(f"Error inserting order_id {row.get('order_id')}: {e}")

            conn.commit()
            logger.info(f"✅ Loaded   : {loaded_count} records into 'sales'")
            logger.info(f"⏭️  Skipped  : {skipped_count} duplicate records")

        # ── Load rejected records ─────────────────────────────────────────
        rejected_count = 0
        if not rejected_df.empty:
            rejected_cols = [
                "order_id", "customer_name", "customer_email",
                "product_name", "category", "quantity", "unit_price",
                "discount_percent", "region", "order_date", "status",
                "rejection_reason"
            ]
            available_rej_cols = [c for c in rejected_cols if c in rejected_df.columns]
            rejected_df[available_rej_cols].to_sql(
                "rejected_sales", conn, if_exists="append", index=False
            )
            rejected_count = len(rejected_df)
            logger.warning(f"⚠️  Rejected : {rejected_count} records into 'rejected_sales'")

        # ── Write audit log ───────────────────────────────────────────────
        audit = {
            "run_at"          : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_file"     : source_file,
            "total_extracted" : loaded_count + rejected_count + skipped_count,
            "total_loaded"    : loaded_count,
            "total_rejected"  : rejected_count,
            "status"          : "SUCCESS"
        }
        pd.DataFrame([audit]).to_sql(
            "etl_audit_log", conn, if_exists="append", index=False
        )
        logger.info("📝 Audit log written.")

        return audit

    except Exception as e:
        logger.error(f"❌ Load failed: {e}")
        # Write failed audit log
        audit = {
            "run_at"          : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_file"     : source_file,
            "total_extracted" : 0,
            "total_loaded"    : 0,
            "total_rejected"  : 0,
            "status"          : f"FAILED: {str(e)}"
        }
        pd.DataFrame([audit]).to_sql(
            "etl_audit_log", conn, if_exists="append", index=False
        )
        raise

    finally:
        conn.close()
