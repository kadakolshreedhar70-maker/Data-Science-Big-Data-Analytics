import os
from datetime import datetime


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
LAKEHOUSE_DIR = os.path.join(DATA_DIR, "lakehouse")
BRONZE_DIR = os.path.join(LAKEHOUSE_DIR, "bronze")
SILVER_DIR = os.path.join(LAKEHOUSE_DIR, "silver")
GOLD_DIR = os.path.join(LAKEHOUSE_DIR, "gold")

LEGACY_FASHION_CSV = os.path.join(DATA_DIR, "fashion_trends.csv")
LEGACY_TRAVEL_CSV = os.path.join(DATA_DIR, "travel_trends.csv")

SILVER_FASHION_PARQUET = os.path.join(SILVER_DIR, "google_trends", "fashion_trends.parquet")
SILVER_TRAVEL_PARQUET = os.path.join(SILVER_DIR, "google_trends", "travel_trends.parquet")

GOLD_TREND_SUMMARY_PARQUET = os.path.join(GOLD_DIR, "trend_summary.parquet")
GOLD_DESTINATION_SCORE_PARQUET = os.path.join(GOLD_DIR, "destination_scores.parquet")


def ensure_data_directories():
    paths = [
        DATA_DIR,
        os.path.dirname(SILVER_FASHION_PARQUET),
        os.path.dirname(SILVER_TRAVEL_PARQUET),        os.path.dirname(GOLD_TREND_SUMMARY_PARQUET),
    ]
    for path in paths:
        os.makedirs(path, exist_ok=True)


def bronze_snapshot_path(source_name, dataset_name, captured_at=None):
    captured_at = captured_at or datetime.utcnow()
    partition = captured_at.strftime("%Y-%m-%d")
    filename = f"{captured_at.strftime('%Y%m%d_%H%M%S')}_{dataset_name}.parquet"
    return os.path.join(BRONZE_DIR, source_name, dataset_name, partition, filename)
