from typing import List

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import (
    BooleanType,
    DateType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    StringType,
    TimestampType,
)

spark = SparkSession.builder.getOrCreate()


# Check table existence
def table_exists(table_path: str) -> bool:
    hconf = spark._jsc.hadoopConfiguration()

    # get the Hadoop FileSystem bound to that config
    fs = spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(hconf)

    # build a Hadoop Path for your ABFSS location
    path = spark.sparkContext._jvm.org.apache.hadoop.fs.Path(f"{table_path}")

    # ask the FileSystem if it’s there
    return fs.exists(path)


# JDBC Postgres reader
def query_postgres_table(
    hostname: str, database: str, table: str, user: str, password: str, port: int = 5432
):
    jdbc_url = f"jdbc:postgresql://{hostname}:{port}/{database}?sslmode=require"
    connection_props = {
        "user": user,
        "password": password,
        "driver": "org.postgresql.Driver",
    }
    return (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", f"public.{table}")
        .options(**connection_props)
        .load()
    )


# Map Spark types to SQL types
def spark_type_to_sql(data_type):
    if isinstance(data_type, StringType):
        return "STRING"
    if isinstance(data_type, IntegerType):
        return "INT"
    if isinstance(data_type, LongType):
        return "BIGINT"
    if isinstance(data_type, DoubleType):
        return "DOUBLE"
    if isinstance(data_type, FloatType):
        return "FLOAT"
    if isinstance(data_type, BooleanType):
        return "BOOLEAN"
    if isinstance(data_type, TimestampType):
        return "TIMESTAMP"
    if isinstance(data_type, DateType):
        return "DATE"
    return data_type.simpleString().upper()


# align dataframe to Delta table schema
def align_df_to_delta_schema(df, table_path: str):
    if table_exists(table_path):
        target_schema = spark.read.format("delta").load(table_path).schema
    else:
        print(f"⚠ Target table at {table_path} does not exist. Using source schema as-is.")
        return df  # Return df unchanged

    df_cols = set(df.columns)
    aligned = df

    for f in target_schema:
        if f.name not in df_cols:
            aligned = aligned.withColumn(f.name, lit(None).cast(f.dataType))

    return aligned.select([f.name for f in target_schema])


# Create/update via DataFrame schema
def create_or_update_table_from_df_schema(df, table_path: str):
    if not table_exists(table_path):
        df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option(
            "path", table_path
        ).save()

        return

    existing = spark.read.format("delta").load(table_path).schema
    existing_fields = {f.name for f in existing.fields}
    additions = [f for f in df.schema.fields if f.name not in existing_fields]
    if not additions:
        print("No schema changes")
        return

    for fld in additions:
        sql_type = spark_type_to_sql(fld.dataType)
        null_clause = "" if fld.nullable else "NOT NULL"
        spark.sql(
            f"ALTER TABLE delta.`{table_path}` ADD COLUMNS ({fld.name} {sql_type} {null_clause})"
        )
        print(f"Added column {fld.name}")


# Merge via SQL
def merge_df_to_table(source_df, target_table_path: str, pk_cols: List[str] | str):
    """
    Upsert (MERGE) source_df into target_table_path deduplicating by pk_cols.

    - source_df: input DataFrame
    - target_table_path: Full abfs path for target Delta table
    - pk_cols: single column name or list of column names representing the key
    """
    # Normalize pk_cols to a list
    if isinstance(pk_cols, str):
        pk_list = [pk_cols]
    else:
        pk_list = pk_cols

    # Deduplicate source on the key columns
    deduped = source_df.dropDuplicates(pk_list)

    # Register staging view
    deduped.createOrReplaceTempView("_stg")

    # Build the ON clause for composite keys
    on_clause = " AND ".join(f"target.{c} = src.{c}" for c in pk_list)

    # Execute the MERGE
    merge_sql = f"""
      MERGE INTO delta.`{target_table_path}` AS target
      USING _stg AS src
        ON {on_clause}
      WHEN MATCHED THEN
        UPDATE SET *
      WHEN NOT MATCHED THEN
        INSERT *
    """
    spark.sql(merge_sql)
    print(f"Merged into delta.`{target_table_path}` deduplicated on {pk_list}")


# Watermark helpers
def get_watermark(wm_table_path: str, table_name: str) -> int:
    df = spark.read.format("delta").load(wm_table_path).filter(col("table_name") == table_name)
    return df.collect()[0]["ts"] if df.count() else 0


def update_watermark(wm_table_path: str, table_name: str, ts: int):
    wm_df = spark.createDataFrame([(table_name, ts)], ["table_name", "ts"])
    wm_df.createOrReplaceTempView("new_wm")
    spark.sql(
        f"""
      MERGE INTO delta.`{wm_table_path}` AS target
      USING new_wm AS src
        ON target.table_name = src.table_name
      WHEN MATCHED THEN UPDATE SET ts = src.ts
      WHEN NOT MATCHED THEN INSERT (table_name, ts) VALUES (src.table_name, src.ts)
    """
    )
    print(f"Watermark for {table_name} set to {ts}")
