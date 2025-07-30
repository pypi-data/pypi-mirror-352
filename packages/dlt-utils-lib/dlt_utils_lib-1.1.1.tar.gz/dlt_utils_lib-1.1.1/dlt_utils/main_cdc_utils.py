from pyspark.sql.functions import col, expr, coalesce, lit, when, current_timestamp
from .dlt_transformations import update_cdc_timestamp, apply_partitions, add_default_value_for_removed_col, rename_columns

# Base code pipeline: streaming process
def base_cdc_replication_process(dlt,
                                 spark,
                                 cdc_tables_map: list, 
                                 bronze_directory: str,
                                 bucket_name: str,
                                 time_diff_history_cdc_timestamp: int = 30):

    # parse list with tables for replication
    for table in cdc_tables_map:
        source_table_name = table['source_table_name']
        source_schema = table['source_schema']
        file_format = table['format']
        keys = table['keys']
        exclude_columns = table['exclude_columns']
        partition_col = table['partition_col']
        enable_truncate = table['enable_truncate']
        s3_files_path = f"{source_schema}/{source_table_name}/"
        bronze_table_path = f"{bucket_name}/{bronze_directory}/{s3_files_path}"
        # Optional parameters
        default_value_for_removed_col = table.get('default_value_for_removed_col', {})




        # Execute pipeline
        create_bronze_table_definition(spark=spark,
                                       dlt=dlt,
                                       table_name=source_table_name,
                                       files_path=bronze_table_path, 
                                       file_format=file_format,
                                       partitions=partition_col,
                                       schema_exclude_columns=exclude_columns,
                                       keys=keys,
                                       time_diff_history_cdc_timestamp=time_diff_history_cdc_timestamp,
                                       default_value_for_removed_col=default_value_for_removed_col
                                        )
        
        silver_streaming_process(dlt=dlt,
                                table_name=source_table_name,
                                keys=keys,
                                partitions=partition_col,
                                exclude_columns=exclude_columns,
                                enable_truncate=enable_truncate)
        

# Define the transformation function dynamically
def create_bronze_table_definition(spark, dlt, table_name: str, files_path: str, file_format: str, partitions: dict, schema_exclude_columns: list, keys: list, time_diff_history_cdc_timestamp: int, default_value_for_removed_col: dict):
    @dlt.table(
        name=f"bronze_{table_name}",
        comment="This is the bronze table.",
        temporary=False
    )
    def transform_cdc_to_bronze():
        df = spark.read.format(file_format).load(files_path).transform(rename_columns)      
        fields = [field for field in df.schema.fields if field.name not in schema_exclude_columns]
        schema_string = ', '.join([f"{field.name} {field.dataType.simpleString()}" for field in fields])
        return spark \
            .readStream \
            .format('cloudFiles') \
            .option("cloudFiles.format", file_format) \
            .option("cloudFiles.schemaHints", schema_string) \
            .option("cloudFiles.inferColumnTypes", "true") \
            .load(files_path) \
            .withColumn('cdc_timestamp', col('cdc_timestamp').cast('timestamp')) \
            .withColumn('ar_h_change_seq', col('ar_h_change_seq').cast('string')) \
            .withColumn('dlt_timestamp', current_timestamp()) \
            .transform(lambda df: update_cdc_timestamp(df, time_diff_history_cdc_timestamp)) \
            .transform(lambda df: apply_partitions(df, partitions)) \
            .transform(lambda df: add_default_value_for_removed_col(df, default_value_for_removed_col))

    return transform_cdc_to_bronze



# Create silver streaming data
def silver_streaming_process(dlt, table_name: str, keys: list, partitions: dict, exclude_columns: list, enable_truncate: bool = False):
    dlt.create_streaming_table(
        name=table_name,
        table_properties={
            "delta.autoOptimize.optimizeWrite": "true",
            "delta.autoOptimize.autoCompact": "true"
        },
        comment = "This is the silver table with source in",
        partition_cols=partitions if partitions else None
    )

    dlt.apply_changes(
        target=table_name,
        source=f"bronze_{table_name}",
        keys=keys,
        sequence_by=col("ar_h_change_seq"),
        apply_as_deletes=expr("Op = 'D'"),
        apply_as_truncates=expr("Op = 'T'") if enable_truncate else None,
        except_column_list=["Op", "_rescued_data"] + exclude_columns,
        stored_as_scd_type=1
    )
