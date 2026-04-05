# data_ingestion/google_trends_fetcher.py
# Fetches fashion and travel trend data with no API key.
# Run: python data_ingestion/google_trends_fetcher.py

import os
import sys
import time
from datetime import datetime

import pandas as pd
from loguru import logger
from pytrends.request import TrendReq

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import (
    GTRENDS_FASHION_KW,
    GTRENDS_GEO,
    GTRENDS_TIMEFRAME,
    GTRENDS_TRAVEL_KW,
    GTRENDS_TRAVEL_LABELS,
)
from utils.data_paths import (
    LEGACY_FASHION_CSV,
    LEGACY_TRAVEL_CSV,
    SILVER_FASHION_PARQUET,
    SILVER_TRAVEL_PARQUET,
    bronze_snapshot_path,
    ensure_data_directories,
)


def get_pytrends_client():
    return TrendReq(hl="en-US", tz=330, timeout=(10, 25), retries=3, backoff_factor=0.5)


def fetch_interest_over_time(keywords, timeframe=None, geo=None):
    """Fetch Google Trends interest data for up to 5 keywords."""
    timeframe = timeframe or GTRENDS_TIMEFRAME
    geo = geo or GTRENDS_GEO
    keywords = keywords[:5]

    client = get_pytrends_client()
    client.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
    df = client.interest_over_time()

    if df.empty:
        logger.warning(f"No data for: {keywords}")
        return pd.DataFrame()

    df = df.drop(columns=["isPartial"], errors="ignore")
    logger.info(f"Fetched {len(df)} rows for: {keywords}")
    return df


def fetch_in_batches(keywords):
    results = {}
    for start in range(0, len(keywords), 5):
        batch = keywords[start:start + 5]
        df = fetch_interest_over_time(batch)
        if not df.empty:
            for column in df.columns:
                results[column] = df[column]
        time.sleep(2)
    return results


def build_trend_dataframe(results, labels_map=None):
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    if labels_map:
        df = df.rename(columns=labels_map)
    df.index.name = "date"
    return df


def build_snapshot_records(df, dataset_name, captured_at):
    if df.empty:
        return pd.DataFrame()

    snapshot = df.reset_index().melt(id_vars="date", var_name="keyword", value_name="score")
    snapshot["date"] = pd.to_datetime(snapshot["date"]).astype("datetime64[ms]")
    snapshot["dataset"] = dataset_name
    snapshot["source"] = "google_trends"
    snapshot["captured_at"] = captured_at.isoformat()
    return snapshot


def save_trend_outputs(fashion_df, travel_df, captured_at):
    ensure_data_directories()

    if not fashion_df.empty:
        fashion_df.to_csv(LEGACY_FASHION_CSV)
        fashion_silver_df = fashion_df.reset_index()
        fashion_silver_df["date"] = pd.to_datetime(fashion_silver_df["date"]).astype("datetime64[ms]")
        fashion_silver_df.to_parquet(SILVER_FASHION_PARQUET, index=False)

        fashion_snapshot = build_snapshot_records(fashion_df, "fashion_trends", captured_at)
        fashion_snapshot_path = bronze_snapshot_path("google_trends", "fashion_trends", captured_at)
        os.makedirs(os.path.dirname(fashion_snapshot_path), exist_ok=True)
        fashion_snapshot.to_parquet(fashion_snapshot_path, index=False)
        logger.info(f"Saved fashion outputs to CSV, silver parquet, and bronze snapshot")

    if not travel_df.empty:
        travel_df.to_csv(LEGACY_TRAVEL_CSV)
        travel_silver_df = travel_df.reset_index()
        travel_silver_df["date"] = pd.to_datetime(travel_silver_df["date"]).astype("datetime64[ms]")
        travel_silver_df.to_parquet(SILVER_TRAVEL_PARQUET, index=False)

        travel_snapshot = build_snapshot_records(travel_df, "travel_trends", captured_at)
        travel_snapshot_path = bronze_snapshot_path("google_trends", "travel_trends", captured_at)
        os.makedirs(os.path.dirname(travel_snapshot_path), exist_ok=True)
        travel_snapshot.to_parquet(travel_snapshot_path, index=False)
        logger.info(f"Saved travel outputs to CSV, silver parquet, and bronze snapshot")


def save_trends_to_csv():
    """Fetch real data and save both dashboard CSVs and Spark-friendly parquet datasets."""
    captured_at = datetime.utcnow()

    print("Fetching fashion trends from Google...")
    fashion_df = build_trend_dataframe(fetch_in_batches(GTRENDS_FASHION_KW))

    print("Fetching travel trends from Google...")
    travel_df = build_trend_dataframe(fetch_in_batches(GTRENDS_TRAVEL_KW), labels_map=GTRENDS_TRAVEL_LABELS)

    save_trend_outputs(fashion_df, travel_df, captured_at)

    if not fashion_df.empty:
        print(f"Saved fashion_trends.csv and parquet datasets - {len(fashion_df)} rows")
    if not travel_df.empty:
        print(f"Saved travel_trends.csv and parquet datasets - {len(travel_df)} rows")

    print("Done! Real data saved to data/ folder.")


if __name__ == "__main__":
    save_trends_to_csv()
