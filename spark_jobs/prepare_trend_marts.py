import os
import sys

from loguru import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_paths import (
    GOLD_DESTINATION_SCORE_PARQUET,
    GOLD_TREND_SUMMARY_PARQUET,
    SILVER_FASHION_PARQUET,
    SILVER_TRAVEL_PARQUET,
    ensure_data_directories,
)


def build_spark_session():
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName("TrendVoyageTrendMarts")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "Asia/Kolkata")
        .getOrCreate()
    )


def build_stack_expression(columns):
    return "stack({0}, {1}) as (name, score)".format(
        len(columns),
        ", ".join([f"'{column}', `{column}`" for column in columns]),
    )


def prepare_trend_marts():
    ensure_data_directories()
    spark = build_spark_session()

    try:
        fashion_df = spark.read.parquet(SILVER_FASHION_PARQUET)
        travel_df = spark.read.parquet(SILVER_TRAVEL_PARQUET)

        from pyspark.sql import functions as F

        fashion_columns = [column for column in fashion_df.columns if column != "date"]
        travel_columns = [column for column in travel_df.columns if column != "date"]

        fashion_long = fashion_df.selectExpr(
            "date",
            build_stack_expression(fashion_columns),
        ).withColumn("category", F.lit("fashion"))

        travel_long = travel_df.selectExpr(
            "date",
            build_stack_expression(travel_columns),
        ).withColumn("category", F.lit("travel"))

        combined = fashion_long.unionByName(travel_long)

        summary_df = (
            combined.groupBy("category", "name")
            .agg(
                F.round(F.avg("score"), 2).alias("avg_score"),
                F.round(F.max("score"), 2).alias("peak_score"),
                F.max("date").alias("latest_date"),
            )
            .orderBy(F.desc("avg_score"))
        )

        destination_scores_df = (
            travel_long.groupBy("name")
            .agg(
                F.round(F.avg("score"), 2).alias("avg_score"),
                F.round(F.avg(F.when(F.month("date").isin([12, 1, 2]), F.col("score"))), 2).alias("winter_score"),
                F.round(F.avg(F.when(F.month("date").isin([3, 4, 5]), F.col("score"))), 2).alias("summer_score"),
                F.round(F.avg(F.when(F.month("date").isin([6, 7, 8]), F.col("score"))), 2).alias("monsoon_score"),
                F.round(F.avg(F.when(F.month("date").isin([9, 10, 11]), F.col("score"))), 2).alias("post_monsoon_score"),
            )
            .orderBy(F.desc("avg_score"))
        )

        summary_df.write.mode("overwrite").parquet(GOLD_TREND_SUMMARY_PARQUET)
        destination_scores_df.write.mode("overwrite").parquet(GOLD_DESTINATION_SCORE_PARQUET)
        logger.info(f"Saved gold trend summary to {GOLD_TREND_SUMMARY_PARQUET}")
        logger.info(f"Saved gold destination scores to {GOLD_DESTINATION_SCORE_PARQUET}")
    finally:
        spark.stop()


if __name__ == "__main__":
    prepare_trend_marts()
