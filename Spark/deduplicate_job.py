from pyspark.sql import functions as F

from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    StringType,
    DoubleType,
    BooleanType
)

# Spark session

df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "device_events")
    .option("startingOffsets", "latest")
    .load()
)

schema = StructType([
    StructField("event_id", LongType(), True),
    StructField("device_id", LongType(), True),
    StructField("event_type", StringType(), True),
    StructField("value", DoubleType(), True),
    StructField("is_valid", BooleanType(), True),
    StructField("event_time", StringType(), True)
])



parsed_df = (
    df 
    .select(
        F.from_json(
            F.col('value').cast('string'),
            schema
        ).alias('data')
    )
    .select('data.*')
    .withColumn(
        'event_time',
        F.to_timestamp('event_time')
    )
)

dedup_df = (
    parsed_df 
    .withWatermark('event_time', '15 minutes')
    .dropDuplicates(['event_id'])
)

query = (
    dedup_df 
    .writeStream
    .format('parquet')
    .option('path', '/lake/raw/device_events')
    .option('checkpointLocation', '/checkpoints/device_events')
    .start()
)