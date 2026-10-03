"""
HTML REPORT MODULE
------------------
Generates a beautiful HTML report with charts from the sales SQLite database.
"""

import sqlite3
import pandas as pd
import logging
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

logger = logging.getLogger(__name__)


def fmt_inr(val):
    try:
        return f"&#8377;{float(val):,.2f}"
    except:
        return val


def df_to_html_table(df):
    headers = "".join(
        f"<th>{col.replace('_', ' ').title()}</th>" for col in df.columns
    )
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{row[col]}</td>" for col in df.columns)
        rows += f"<tr>{cells}</tr>"
    return f"""
    <table>
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def generate_charts(db_path: str, report_dir: str) -> dict:
    """Generate bar/line/pie charts and save as PNG images."""
    conn = sqlite3.connect(db_path)
    charts = {}

    # ── Chart 1: Revenue by Category ─────────────────────────────────────
    df1 = pd.read_sql_query("""
        SELECT category, ROUND(SUM(net_amount), 2) AS net_revenue
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY category ORDER BY net_revenue DESC
    """, conn)

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(df1["category"], df1["net_revenue"],
                  color=["#4f46e5", "#0891b2", "#059669", "#d97706"])
    ax.set_title("Net Revenue by Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Category")
    ax.set_ylabel("Net Revenue")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    path1 = os.path.join(report_dir, "chart_category.png")
    plt.savefig(path1, dpi=150, bbox_inches="tight")
    plt.close()
    charts["category"] = "chart_category.png"

    # ── Chart 2: Revenue by Region ────────────────────────────────────────
    df2 = pd.read_sql_query("""
        SELECT region, ROUND(SUM(net_amount), 2) AS net_revenue
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY region ORDER BY net_revenue DESC
    """, conn)

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(df2["region"], df2["net_revenue"],
                  color=["#7c3aed", "#db2777", "#059669", "#d97706"])
    ax.set_title("Net Revenue by Region", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Region")
    ax.set_ylabel("Net Revenue")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    path2 = os.path.join(report_dir, "chart_region.png")
    plt.savefig(path2, dpi=150, bbox_inches="tight")
    plt.close()
    charts["region"] = "chart_region.png"

    # ── Chart 3: Monthly Sales Trend ──────────────────────────────────────
    df3 = pd.read_sql_query("""
        SELECT SUBSTR(order_date, 1, 7) AS month,
               ROUND(SUM(net_amount), 2) AS net_revenue
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY month ORDER BY month
    """, conn)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(df3["month"], df3["net_revenue"],
            marker="o", color="#4f46e5", linewidth=2.5, markersize=8)
    ax.fill_between(range(len(df3)), df3["net_revenue"], alpha=0.1, color="#4f46e5")
    ax.set_xticks(range(len(df3)))
    ax.set_xticklabels(df3["month"])
    ax.set_title("Monthly Sales Trend", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Revenue")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for i, (x, y) in enumerate(zip(range(len(df3)), df3["net_revenue"])):
        ax.text(x, y + 2000, f"{y:,.0f}", ha="center", fontsize=9)
    plt.tight_layout()
    path3 = os.path.join(report_dir, "chart_monthly.png")
    plt.savefig(path3, dpi=150, bbox_inches="tight")
    plt.close()
    charts["monthly"] = "chart_monthly.png"

    # ── Chart 4: Order Status Pie Chart ───────────────────────────────────
    df4 = pd.read_sql_query("""
        SELECT status, COUNT(*) AS count
        FROM sales GROUP BY status
    """, conn)

    fig, ax = plt.subplots(figsize=(6, 5))
    colors = {"COMPLETED": "#059669", "PENDING": "#d97706", "CANCELLED": "#dc2626"}
    pie_colors = [colors.get(s, "#94a3b8") for s in df4["status"]]
    wedges, texts, autotexts = ax.pie(
        df4["count"], labels=df4["status"],
        autopct="%1.1f%%", colors=pie_colors,
        startangle=90, pctdistance=0.85
    )
    for text in autotexts:
        text.set_fontsize(11)
        text.set_fontweight("bold")
    ax.set_title("Order Status Distribution", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    path4 = os.path.join(report_dir, "chart_status.png")
    plt.savefig(path4, dpi=150, bbox_inches="tight")
    plt.close()
    charts["status"] = "chart_status.png"

    conn.close()
    logger.info(f"✅ Generated {len(charts)} charts")
    return charts


def generate_html_report(db_path: str, report_dir: str) -> str:
    logger.info("Generating HTML report...")
    os.makedirs(report_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")
    report_path = os.path.join(report_dir, f"sales_report_{timestamp}.html")

    summary = pd.read_sql_query("""
        SELECT COUNT(*) AS total_orders, SUM(quantity) AS total_units_sold,
               ROUND(SUM(gross_amount), 2) AS gross_revenue,
               ROUND(SUM(discount_amount), 2) AS discount_given,
               ROUND(SUM(net_amount), 2) AS net_revenue,
               ROUND(AVG(net_amount), 2) AS avg_order_value
        FROM sales WHERE status = 'COMPLETED'
    """, conn)

    by_category = pd.read_sql_query("""
        SELECT category, COUNT(*) AS orders, SUM(quantity) AS units_sold,
               ROUND(SUM(net_amount), 2) AS net_revenue
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY category ORDER BY net_revenue DESC
    """, conn)

    by_region = pd.read_sql_query("""
        SELECT region, COUNT(*) AS orders,
               ROUND(SUM(net_amount), 2) AS net_revenue,
               ROUND(AVG(net_amount), 2) AS avg_order_value
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY region ORDER BY net_revenue DESC
    """, conn)

    top_products = pd.read_sql_query("""
        SELECT product_name, category, SUM(quantity) AS units_sold,
               ROUND(SUM(net_amount), 2) AS net_revenue
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY product_name ORDER BY net_revenue DESC LIMIT 5
    """, conn)

    monthly = pd.read_sql_query("""
        SELECT SUBSTR(order_date, 1, 7) AS month, COUNT(*) AS orders,
               ROUND(SUM(net_amount), 2) AS net_revenue
        FROM sales WHERE status = 'COMPLETED'
        GROUP BY month ORDER BY month
    """, conn)

    status_df = pd.read_sql_query("""
        SELECT status, COUNT(*) AS count,
               ROUND(SUM(net_amount), 2) AS total_value
        FROM sales GROUP BY status ORDER BY count DESC
    """, conn)

    audit_df = pd.read_sql_query("""
        SELECT run_at, source_file, total_extracted,
               total_loaded, total_rejected, status
        FROM etl_audit_log ORDER BY id DESC LIMIT 5
    """, conn)

    conn.close()

    # Generate charts
    charts = generate_charts(db_path, report_dir)

    s = summary.iloc[0]
    cards_data = [
        ("🛒", "Total Orders",    int(s["total_orders"]),       "#4f46e5"),
        ("📦", "Units Sold",      int(s["total_units_sold"]),    "#0891b2"),
        ("💰", "Gross Revenue",   fmt_inr(s["gross_revenue"]),   "#059669"),
        ("🏷️",  "Discount Given", fmt_inr(s["discount_given"]),  "#d97706"),
        ("📈", "Net Revenue",     fmt_inr(s["net_revenue"]),     "#7c3aed"),
        ("🧾", "Avg Order Value", fmt_inr(s["avg_order_value"]), "#db2777"),
    ]

    cards_html = ""
    for icon, label, value, color in cards_data:
        cards_html += f"""
        <div class="card" style="border-top:4px solid {color}">
            <div class="card-icon">{icon}</div>
            <div class="card-value" style="color:{color}">{value}</div>
            <div class="card-label">{label}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Sales ETL Report</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',sans-serif; background:#f1f5f9; color:#1e293b; }}
  header {{
    background: linear-gradient(135deg, #1e3a5f, #4f46e5);
    color:white; padding:40px;
    display:flex; justify-content:space-between; align-items:center;
  }}
  header h1 {{ font-size:28px; font-weight:700; }}
  header p  {{ font-size:13px; opacity:0.8; margin-top:6px; }}
  .badge {{ background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:20px; font-size:13px; font-weight:600; }}
  .container {{ max-width:1200px; margin:0 auto; padding:30px 20px; }}
  .cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-bottom:30px; }}
  .card {{ background:white; border-radius:12px; padding:24px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.08); transition:transform 0.2s; }}
  .card:hover {{ transform:translateY(-4px); }}
  .card-icon  {{ font-size:32px; margin-bottom:10px; }}
  .card-value {{ font-size:22px; font-weight:700; margin-bottom:6px; }}
  .card-label {{ font-size:13px; color:#64748b; font-weight:500; }}
  .section {{ background:white; border-radius:12px; padding:28px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
  .section h2 {{ font-size:17px; font-weight:700; margin-bottom:20px; color:#1e293b; border-left:4px solid #4f46e5; padding-left:12px; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  th {{ background:#f8fafc; color:#475569; font-weight:600; padding:12px 16px; text-align:left; border-bottom:2px solid #e2e8f0; }}
  td {{ padding:12px 16px; border-bottom:1px solid #f1f5f9; color:#334155; }}
  tr:hover td {{ background:#f8fafc; }}
  tr:last-child td {{ border-bottom:none; }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-bottom:24px; }}
  footer {{ text-align:center; padding:24px; color:#94a3b8; font-size:13px; }}
  img {{ width:100%; border-radius:8px; }}
</style>
</head>
<body>

<header>
  <div>
    <h1>📊 Sales ETL Pipeline — Analytics Report</h1>
    <p>Generated on {generated_at}</p>
  </div>
  <div class="badge">✅ Pipeline: SUCCESS</div>
</header>

<div class="container">

  <!-- Summary Cards -->
  <div class="cards">{cards_html}</div>

  <!-- Charts -->
  <div class="two-col">
    <div class="section">
      <h2>📊 Revenue by Category</h2>
      <img src="{charts['category']}" alt="Revenue by Category"/>
    </div>
    <div class="section">
      <h2>🗺️ Revenue by Region</h2>
      <img src="{charts['region']}" alt="Revenue by Region"/>
    </div>
  </div>

  <div class="two-col">
    <div class="section">
      <h2>📅 Monthly Sales Trend</h2>
      <img src="{charts['monthly']}" alt="Monthly Trend"/>
    </div>
    <div class="section">
      <h2>🥧 Order Status Distribution</h2>
      <img src="{charts['status']}" alt="Order Status"/>
    </div>
  </div>

  <!-- Tables -->
  <div class="two-col">
    <div class="section">
      <h2>Revenue by Category</h2>
      {df_to_html_table(by_category)}
    </div>
    <div class="section">
      <h2>Revenue by Region</h2>
      {df_to_html_table(by_region)}
    </div>
  </div>

  <div class="section">
    <h2>🏆 Top 5 Best-Selling Products</h2>
    {df_to_html_table(top_products)}
  </div>

  <div class="two-col">
    <div class="section">
      <h2>📅 Monthly Sales Trend</h2>
      {df_to_html_table(monthly)}
    </div>
    <div class="section">
      <h2>📋 Order Status Breakdown</h2>
      {df_to_html_table(status_df)}
    </div>
  </div>

  <div class="section">
    <h2>🔍 ETL Audit Log</h2>
    {df_to_html_table(audit_df)}
  </div>

</div>

<footer>
  Sales ETL Pipeline &mdash; Built with Python, Pandas &amp; SQLite &nbsp;|&nbsp; Rohan &copy; 2024
</footer>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"✅ HTML report saved: {report_path}")
    return report_path
