"""
Builds a SQLite database from the raw Olist CSV files.

Expects the following CSVs to be placed in ../data/ before running
(download from Kaggle - see README for links):
    olist_marketing_qualified_leads_dataset.csv
    olist_closed_deals_dataset.csv
    olist_orders_dataset.csv
    olist_order_items_dataset.csv
    olist_sellers_dataset.csv
"""
import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = Path(__file__).parent.parent / "olist_funnel.db"

TABLES = {
    "mql": "olist_marketing_qualified_leads_dataset.csv",
    "closed_deals": "olist_closed_deals_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
}


def build_database() -> None:
    conn = sqlite3.connect(DB_PATH)
    for table_name, filename in TABLES.items():
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing {csv_path}. Download the Olist datasets from Kaggle "
                f"and place the CSVs in the data/ folder (see README)."
            )
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded {table_name}: {df.shape[0]} rows")
    conn.close()
    print(f"\nDatabase built at {DB_PATH}")


if __name__ == "__main__":
    build_database()
