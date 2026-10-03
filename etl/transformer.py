"""
TRANSFORM MODULE
----------------
Cleans, validates, and enriches the raw sales DataFrame.
"""

import pandas as pd
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

VALID_STATUSES = {"COMPLETED", "PENDING", "CANCELLED"}


def _safe_str(val):
    """Convert value to string, return None if NaN."""
    if pd.isna(val):
        return None
    return str(val).strip()


def transform(df: pd.DataFrame) -> tuple:
    logger.info("🔄 Starting transformation...")
    original_count = len(df)

    # Work row-by-row for maximum reliability across pandas versions
    clean_rows    = []
    rejected_rows = []

    for _, row in df.iterrows():
        raw = {col: _safe_str(row[col]) for col in df.columns}
        reasons = []

        # ── VALIDATE critical fields ──────────────────────────────────────
        if not raw.get("order_id"):
            reasons.append("Missing order_id")
        if not raw.get("customer_name"):
            reasons.append("Missing customer_name")
        if not raw.get("product_name"):
            reasons.append("Missing product_name")

        # ── VALIDATE & cast numeric fields ────────────────────────────────
        order_id   = None
        quantity   = None
        unit_price = None
        discount   = 0.0

        if not reasons:  # only attempt if critical fields are present
            try:
                order_id = int(float(raw["order_id"]))
            except (TypeError, ValueError):
                reasons.append("Invalid order_id (not a number)")

            try:
                quantity = int(float(raw["quantity"]))
            except (TypeError, ValueError):
                reasons.append("Invalid quantity (not a number)")

            try:
                unit_price = float(raw["unit_price"])
            except (TypeError, ValueError):
                reasons.append("Invalid unit_price (not a number)")

            try:
                discount = float(raw["discount_percent"]) if raw.get("discount_percent") else 0.0
            except (TypeError, ValueError):
                discount = 0.0

        # ── VALIDATE date ─────────────────────────────────────────────────
        order_date = None
        if not reasons:
            try:
                order_date = pd.to_datetime(raw["order_date"]).strftime("%Y-%m-%d")
            except Exception:
                reasons.append("Invalid order_date format")

        # ── REJECT if any errors ──────────────────────────────────────────
        if reasons:
            rejected_row = dict(raw)
            rejected_row["rejection_reason"] = "; ".join(reasons)
            rejected_rows.append(rejected_row)
            continue

        # ── DEFAULTS for optional fields ──────────────────────────────────
        customer_email = raw.get("customer_email") or "N/A"
        region         = raw.get("region") or "Unknown"
        category       = raw.get("category") or "General"
        status         = (raw.get("status") or "PENDING").upper()
        if status not in VALID_STATUSES:
            status = "PENDING"

        # ── CALCULATE derived fields ──────────────────────────────────────
        gross_amount    = round(quantity * unit_price, 2)
        discount_amount = round(gross_amount * discount / 100, 2)
        net_amount      = round(gross_amount - discount_amount, 2)

        # ── BUILD clean row ───────────────────────────────────────────────
        clean_rows.append({
            "order_id":         order_id,
            "customer_name":    raw["customer_name"].title(),
            "customer_email":   customer_email,
            "product_name":     raw["product_name"].title(),
            "category":         category.title(),
            "quantity":         quantity,
            "unit_price":       unit_price,
            "discount_percent": discount,
            "gross_amount":     gross_amount,
            "discount_amount":  discount_amount,
            "net_amount":       net_amount,
            "region":           region.title(),
            "order_date":       order_date,
            "status":           status,
        })

    clean_df    = pd.DataFrame(clean_rows)
    rejected_df = pd.DataFrame(rejected_rows)

    logger.info(f"✅ Clean records    : {len(clean_df)}")
    logger.warning(f"⚠️  Rejected records : {len(rejected_df)}")
    logger.info(f"📊 Total processed  : {original_count}")

    return clean_df, rejected_df
