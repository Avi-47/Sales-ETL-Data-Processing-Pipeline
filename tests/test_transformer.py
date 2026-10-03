"""
TESTS — Transformer Module (unittest)
"""
import unittest
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from etl.transformer import transform


def make_row(**kwargs):
    defaults = {
        "order_id": "1001", "customer_name": "Test User",
        "customer_email": "test@gmail.com", "product_name": "Test Product",
        "category": "Electronics", "quantity": "2", "unit_price": "5000.00",
        "discount_percent": "10", "region": "North",
        "order_date": "2024-01-15", "status": "COMPLETED",
    }
    defaults.update(kwargs)
    return pd.DataFrame([defaults])


class TestTransformer(unittest.TestCase):

    # ── Valid record tests ────────────────────────────────────────────────
    def test_valid_record_passes(self):
        clean, rejected = transform(make_row())
        self.assertEqual(len(clean), 1)
        self.assertEqual(len(rejected), 0)

    def test_gross_amount_calculated(self):
        clean, _ = transform(make_row(quantity="4", unit_price="1000", discount_percent="0"))
        self.assertEqual(clean.iloc[0]["gross_amount"], 4000.0)

    def test_net_amount_after_discount(self):
        clean, _ = transform(make_row(quantity="2", unit_price="1000", discount_percent="10"))
        self.assertEqual(clean.iloc[0]["gross_amount"],    2000.0)
        self.assertEqual(clean.iloc[0]["discount_amount"], 200.0)
        self.assertEqual(clean.iloc[0]["net_amount"],      1800.0)

    def test_customer_name_title_cased(self):
        clean, _ = transform(make_row(customer_name="rahul sharma"))
        self.assertEqual(clean.iloc[0]["customer_name"], "Rahul Sharma")

    def test_status_uppercased(self):
        clean, _ = transform(make_row(status="completed"))
        self.assertEqual(clean.iloc[0]["status"], "COMPLETED")

    def test_date_formatted_correctly(self):
        clean, _ = transform(make_row(order_date="2024-03-10"))
        self.assertEqual(clean.iloc[0]["order_date"], "2024-03-10")

    # ── Rejection tests ───────────────────────────────────────────────────
    def test_missing_order_id_rejected(self):
        _, rejected = transform(make_row(order_id=np.nan))
        self.assertEqual(len(rejected), 1)
        self.assertIn("order_id", rejected.iloc[0]["rejection_reason"])

    def test_missing_customer_name_rejected(self):
        _, rejected = transform(make_row(customer_name=np.nan))
        self.assertEqual(len(rejected), 1)

    def test_missing_product_name_rejected(self):
        _, rejected = transform(make_row(product_name=np.nan))
        self.assertEqual(len(rejected), 1)

    def test_invalid_quantity_rejected(self):
        _, rejected = transform(make_row(quantity="abc"))
        self.assertEqual(len(rejected), 1)

    def test_invalid_unit_price_rejected(self):
        _, rejected = transform(make_row(unit_price="not-a-price"))
        self.assertEqual(len(rejected), 1)

    def test_invalid_date_rejected(self):
        _, rejected = transform(make_row(order_date="bad-date"))
        self.assertEqual(len(rejected), 1)

    # ── Default fill tests ────────────────────────────────────────────────
    def test_missing_email_filled_with_na(self):
        clean, _ = transform(make_row(customer_email=np.nan))
        self.assertEqual(clean.iloc[0]["customer_email"], "N/A")

    def test_zero_discount_when_missing(self):
        clean, _ = transform(make_row(discount_percent=np.nan))
        self.assertEqual(clean.iloc[0]["discount_percent"], 0)

    def test_invalid_status_normalized_to_pending(self):
        clean, _ = transform(make_row(status="SHIPPED"))
        self.assertEqual(clean.iloc[0]["status"], "PENDING")

    # ── Batch test ────────────────────────────────────────────────────────
    def test_mixed_batch(self):
        rows = pd.concat([
            make_row(order_id="2001"),
            make_row(order_id="2002", customer_name=np.nan),
            make_row(order_id="2003", quantity="abc"),
            make_row(order_id="2004"),
        ], ignore_index=True)
        clean, rejected = transform(rows)
        self.assertEqual(len(clean), 2)
        self.assertEqual(len(rejected), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
