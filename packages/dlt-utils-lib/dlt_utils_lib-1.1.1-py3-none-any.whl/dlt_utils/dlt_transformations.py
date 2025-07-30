from pyspark.sql import DataFrame
from pyspark.sql.types import TimestampType, DateType
from pyspark.sql.functions import col, expr, greatest, when, datediff, lag, min as spark_min, expr, count, coalesce
from pyspark.sql.window import Window


def apply_partitions(df: DataFrame, partitions: dict):
    # apply partitioning to the dataframe
    if partitions:
        for col_name, expression in partitions.items():
            if expression.replace(" ", "") != '':
                df = df.withColumn(col_name, expr(expression))
    return df
    
def update_cdc_timestamp(df: DataFrame, time_diff_threshold: int) -> DataFrame:
    # if cdc_timestamp is null or time difference is greater than threshold, set it to the max timestamp in the row
    timestamp_cols = [col.name for col in df.schema.fields if isinstance(col.dataType, (TimestampType, DateType)) and col.name not in  ['cdc_timestamp', 'commit_timestamp', 'dlt_timestamp']]

    if timestamp_cols:
        max_timestamp_per_row = None

        if len(timestamp_cols) > 1:
            max_timestamp_per_row = greatest(*[col(col_name) for col_name in timestamp_cols])
            # temp fix for market table if possible need take last_update_date becouse of market table contnin close time
            if 'last_update_date' in timestamp_cols:
                max_timestamp_per_row = when(
                                                col('last_update_date').isNotNull(), 
                                                col('last_update_date')
                                            ).otherwise(max_timestamp_per_row)
            # temp fix for artemis table if possible need take last_update_date becouse of market table contnin close time
            if 'version' in timestamp_cols:
                max_timestamp_per_row = when(
                                                col('version').isNotNull(), 
                                                col('version')
                                            ).otherwise(max_timestamp_per_row)        
        else:
            max_timestamp_per_row = col(timestamp_cols[0])
            
        df = df.withColumn(
            'cdc_timestamp',
                when(
                    (col('cdc_timestamp').isNull()) | 
                    (datediff(col('cdc_timestamp'), max_timestamp_per_row) > time_diff_threshold), 
                    max_timestamp_per_row
                ).otherwise(col('cdc_timestamp'))
            )
    return df


def add_default_value_for_removed_col(df: DataFrame, default_value_for_removed_col: dict) -> DataFrame:
    if default_value_for_removed_col:
        if default_value_for_removed_col['name'] in df.columns:
            df = df.withColumn(default_value_for_removed_col['name'], when(col(default_value_for_removed_col['name']).isNull(), expr(default_value_for_removed_col['expr'])).otherwise(col(default_value_for_removed_col['name'])))
        else:
            df = df.withColumn(default_value_for_removed_col['name'], expr(default_value_for_removed_col['expr']))
    return df


def rename_columns(df: DataFrame) -> DataFrame:
    new_columns = [col.replace('.', '_') for col in df.columns]
    return df.toDF(*new_columns)




