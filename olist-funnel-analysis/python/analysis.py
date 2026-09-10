"""
Runs the funnel SQL queries against olist_funnel.db and saves chart images
to ../charts/. Run build_database.py first.
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = Path(__file__).parent.parent / "olist_funnel.db"
CHARTS_DIR = Path(__file__).parent.parent / "charts"

OVERALL_FUNNEL_SQL = """
SELECT
    'Lead (MQL)' AS stage, (SELECT COUNT(*) FROM mql) AS count
UNION ALL
SELECT
    'Deal Won', (SELECT COUNT(DISTINCT mql_id) FROM closed_deals)
UNION ALL
SELECT
    'First Sale',
    (SELECT COUNT(DISTINCT cd.mql_id) FROM closed_deals cd
     JOIN order_items oi ON oi.seller_id = cd.seller_id);
"""

BY_ORIGIN_SQL = """
SELECT
    m.origin,
    COUNT(DISTINCT m.mql_id) AS leads,
    COUNT(DISTINCT cd.mql_id) AS deals_won,
    ROUND(COUNT(DISTINCT cd.mql_id) * 1.0 / COUNT(DISTINCT m.mql_id), 4) AS conversion_rate
FROM mql m
LEFT JOIN closed_deals cd ON cd.mql_id = m.mql_id
WHERE m.origin IS NOT NULL
GROUP BY m.origin
HAVING leads >= 100
ORDER BY conversion_rate DESC;
"""

BY_SEGMENT_SQL = """
SELECT
    cd.business_segment,
    COUNT(DISTINCT cd.mql_id) AS deals_won,
    ROUND(COUNT(DISTINCT CASE WHEN oi.seller_id IS NOT NULL THEN cd.mql_id END) * 1.0
          / COUNT(DISTINCT cd.mql_id), 4) AS conversion_rate
FROM closed_deals cd
LEFT JOIN order_items oi ON oi.seller_id = cd.seller_id
WHERE cd.business_segment IS NOT NULL
GROUP BY cd.business_segment
HAVING deals_won >= 20
ORDER BY conversion_rate DESC;
"""


def plot_overall_funnel(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(OVERALL_FUNNEL_SQL, conn)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(df["stage"], df["count"], color=["#4C72B0", "#DD8452", "#55A868"])
    for i, v in enumerate(df["count"]):
        ax.text(i, v + 100, str(v), ha="center", fontweight="bold")
    ax.set_title("Olist Seller Funnel: Lead → Deal Won → First Sale")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "funnel_overview.png", dpi=150)
    print(df)


def plot_conversion_by_origin(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(BY_ORIGIN_SQL, conn)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df["origin"], df["conversion_rate"], color="#4C72B0")
    ax.set_xlabel("Lead \u2192 Deal Won conversion rate")
    ax.set_title("Conversion Rate by Lead Origin")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "conversion_by_origin.png", dpi=150)
    print(df)


def plot_conversion_by_segment(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(BY_SEGMENT_SQL, conn)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df["business_segment"], df["conversion_rate"], color="#DD8452")
    ax.set_xlabel("Deal Won \u2192 First Sale conversion rate")
    ax.set_title("Conversion Rate by Business Segment")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "conversion_by_segment.png", dpi=150)
    print(df)


def main() -> None:
    CHARTS_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    plot_overall_funnel(conn)
    plot_conversion_by_origin(conn)
    plot_conversion_by_segment(conn)
    conn.close()
    print(f"\nCharts saved to {CHARTS_DIR}")


if __name__ == "__main__":
    main()
