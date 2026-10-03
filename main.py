"""
SALES ETL PIPELINE — MAIN ENTRY POINT
======================================
Orchestrates the full ETL flow:
  Extract  → Read raw CSV
  Transform → Clean, validate, enrich
  Load      → Write to SQLite
  Report    → Generate analytics report

Usage:
  python main.py
  python main.py --input data/sales_data.csv --db sales.db
"""

import argparse
import sys
import time
from etl import setup_logger, extract, transform, load, generate_report, generate_html_report


# ── Config Defaults ────────────────────────────────────────────────────────────
DEFAULT_INPUT_FILE = "data/sales_data.csv"
DEFAULT_DB_PATH    = "sales_etl.db"
DEFAULT_REPORT_DIR = "reports"
DEFAULT_LOG_DIR    = "logs"


def parse_args():
    parser = argparse.ArgumentParser(description="Sales ETL Pipeline")
    parser.add_argument("--input",   default=DEFAULT_INPUT_FILE, help="Path to input CSV")
    parser.add_argument("--db",      default=DEFAULT_DB_PATH,    help="Path to SQLite DB")
    parser.add_argument("--reports", default=DEFAULT_REPORT_DIR, help="Reports output directory")
    parser.add_argument("--logs",    default=DEFAULT_LOG_DIR,    help="Logs directory")
    parser.add_argument("--no-report", action="store_true",      help="Skip report generation")
    return parser.parse_args()


def run_pipeline(input_file: str, db_path: str, report_dir: str, generate: bool = True):
    logger = setup_logger()

    logger.info("=" * 60)
    logger.info("   SALES ETL PIPELINE STARTED")
    logger.info("=" * 60)

    start_time = time.time()

    try:
        # ── EXTRACT ───────────────────────────────────────────────────
        logger.info("[ STEP 1 ] EXTRACT")
        raw_df = extract(input_file)

        # ── TRANSFORM ─────────────────────────────────────────────────
        logger.info("[ STEP 2 ] TRANSFORM")
        clean_df, rejected_df = transform(raw_df)

        if not rejected_df.empty:
            rejected_path = "data/rejected_records.csv"
            rejected_df.to_csv(rejected_path, index=False)
            logger.warning(f"⚠️  Rejected records saved to: {rejected_path}")

        # ── LOAD ──────────────────────────────────────────────────────
        logger.info("[ STEP 3 ] LOAD")
        audit = load(clean_df, rejected_df, db_path, input_file)

        # ── REPORT ────────────────────────────────────────────────────
        if generate:
            logger.info("[ STEP 4 ] REPORT")
            report_path = generate_report(db_path, report_dir)
            html_path = generate_html_report(db_path, report_dir)

        # ── SUMMARY ───────────────────────────────────────────────────
        elapsed = round(time.time() - start_time, 2)

        logger.info("=" * 60)
        logger.info("   PIPELINE COMPLETED SUCCESSFULLY ✅")
        logger.info(f"   Total Extracted : {audit['total_extracted']}")
        logger.info(f"   Total Loaded    : {audit['total_loaded']}")
        logger.info(f"   Total Rejected  : {audit['total_rejected']}")
        logger.info(f"   Time Taken      : {elapsed}s")
        logger.info("=" * 60)

        return True

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        input_file=args.input,
        db_path=args.db,
        report_dir=args.reports,
        generate=not args.no_report
    )
