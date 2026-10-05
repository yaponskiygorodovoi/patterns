from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
import logging
import sys


# -------------------------
# Logging
# -------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# -------------------------
# Spark initialization
# -------------------------

def create_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("orders_daily_revenue")
        .config("spark.sql.shuffle.partitions", "200")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )


# -------------------------
# Extract
# -------------------------

def read_orders(
    spark: SparkSession,
    path: str
) -> DataFrame:

    logger.info("Reading orders from %s", path)

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .csv(path)
    )

    return df


# -------------------------
# Transform
# -------------------------

def clean_orders(df: DataFrame) -> DataFrame:

    return (
        df
        .select(
            F.col("order_id").cast("long").alias("order_id"),
            F.col("user_id").cast("long").alias("user_id"),
            F.col("amount").cast("double").alias("amount"),
            F.to_timestamp("created_at").alias("created_at")
        )
        .filter(F.col("order_id").isNotNull())
        .filter(F.col("user_id").isNotNull())
        .filter(F.col("amount") > 0)
        .filter(F.col("created_at").isNotNull())
        .dropDuplicates(["order_id"])
    )


def calculate_daily_revenue(df: DataFrame) -> DataFrame:

    return (
        df
        .withColumn(
            "order_date",
            F.to_date("created_at")
        )
        .groupBy(
            "order_date",
            "user_id"
        )
        .agg(
            F.sum("amount").alias("revenue"),
            F.count("*").alias("orders_count")
        )
    )


# -------------------------
# Load
# -------------------------

def write_result(
    df: DataFrame,
    path: str
) -> None:

    logger.info("Writing result to %s", path)

    (
        df.write
        .mode("overwrite")
        .partitionBy("order_date")
        .parquet(path)
    )


# -------------------------
# Main
# -------------------------

def main():

    input_path = "s3a://raw/orders/"
    output_path = "s3a://mart/daily_revenue/"

    spark = None

    try:

        spark = create_spark()

        logger.info("Spark job started")

        orders = read_orders(
            spark,
            input_path
        )

        clean = clean_orders(orders)

        result = calculate_daily_revenue(clean)

        write_result(
            result,
            output_path
        )

        logger.info("Spark job completed successfully")

    except Exception:
        logger.exception("Spark job failed")
        raise

    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    main()