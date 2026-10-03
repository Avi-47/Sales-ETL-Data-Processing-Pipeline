"""
EXTRACT MODULE
--------------
Reads raw sales data from CSV file into a Pandas DataFrame.
"""

import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


def extract(file_path: str) -> pd.DataFrame:
   
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    logger.info(f"📥 Extracting data from: {file_path}")

    df = pd.read_csv(file_path, dtype=str)  # Read everything as string (safe raw extract)
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names

    logger.info(f"✅ Extracted {len(df)} raw records from CSV.")
    return df
