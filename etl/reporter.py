"""
REPORT MODULE
-------------

"""

import sqlite3
import pandas as pd
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_report(db_path: str, report_dir: str) -> str:
    """
    Query the sales database and generate a text + CSV report.

    Args:
        db_path    : Path to the SQLite database.
        report_dir : Directory to save the report files.

    Returns:
        Path to the generated text report.
    """
    logger.info("📊 Generating sales report...")
    os.makedirs(report_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"sales_report_{timestamp}.txt")

    queries = {
        "1. Total Sales Summary": """
            SELECT
                COUNT(*)                        AS total_orders,
                SUM(quantity)                   AS total_units_sold,
                ROUND(SUM(gross_amount), 2)     AS total_gross_revenue,
                ROUND(SUM(discount_amount), 2)  AS total_discount_given,
                ROUND(SUM(net_amount), 2)       AS total_net_revenue,
                ROUND(AVG(net_amount), 2)       AS avg_order_value
            FROM sales
            WHERE status = 'COMPLETED'
        """,

        "2. Revenue by Category": """
            SELECT
                category,
                COUNT(*)                        AS total_orders,
                SUM(quantity)                   AS units_sold,
                ROUND(SUM(net_amount), 2)       AS net_revenue
            FROM sales
            WHERE status = 'COMPLETED'
            GROUP BY category
            ORDER BY net_revenue DESC
        """,

        "3. Revenue by Region": """
            SELECT
                region,
                COUNT(*)                        AS total_orders,
                ROUND(SUM(net_amount), 2)       AS net_revenue,
                ROUND(AVG(net_amount), 2)       AS avg_order_value
            FROM sales
            WHERE status = 'COMPLETED'
            GROUP BY region
            ORDER BY net_revenue DESC
        """,

        "4. Top 5 Best-Selling Products": """
            SELECT
                product_name,
                category,
                SUM(quantity)                   AS units_sold,
                ROUND(SUM(net_amount), 2)       AS net_revenue
            FROM sales
            WHERE status = 'COMPLETED'
            GROUP BY product_name, category
            ORDER BY units_sold DESC
            LIMIT 5
        """,

        "5. Monthly Sales Trend": """
            SELECT
                SUBSTR(order_date, 1, 7)        AS month,
                COUNT(*)                        AS total_orders,
                ROUND(SUM(net_amount), 2)       AS net_revenue
            FROM sales
            WHERE status = 'COMPLETED'
            GROUP BY month
            ORDER BY month
        """,

        "6. Order Status Breakdown": """
            SELECT
                status,
                COUNT(*)                        AS count,
                ROUND(SUM(net_amount), 2)       AS total_value
            FROM sales
            GROUP BY status
            ORDER BY count DESC
        """,

        "7. ETL Audit Log": """
            SELECT * FROM etl_audit_log
            ORDER BY id DESC
            LIMIT 5
        """
    }

    report_lines = []
    report_lines.append("=" * 65)
    report_lines.append("           SALES ETL PIPELINE — ANALYTICS REPORT")
    report_lines.append(f"           Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 65)

    for title, sql in queries.items():
        try:
            df = pd.read_sql_query(sql.strip(), conn)
            report_lines.append(f"\n{'─'*65}")
            report_lines.append(f"  {title}")
            report_lines.append(f"{'─'*65}")
            report_lines.append(df.to_string(index=False))

            # Save each query result as CSV too
            csv_name = title.split(".")[1].strip().lower().replace(" ", "_")
            df.to_csv(
                os.path.join(report_dir, f"{csv_name}_{timestamp}.csv"),
                index=False
            )
        except Exception as e:
            report_lines.append(f"  [Error running query: {e}]")

    report_lines.append(f"\n{'='*65}")
    report_lines.append("  END OF REPORT")
    report_lines.append(f"{'='*65}\n")

    conn.close()

    report_text = "\n".join(report_lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Print to console too
    print(report_text)
    logger.info(f"✅ Report saved to: {report_path}")

    return report_path
