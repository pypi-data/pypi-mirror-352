import sys
import os
import pytest
from unittest import mock
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import expr
from pyspark.sql.types import TimestampType, StringType
from datetime import datetime
from dlt_utils.dlt_transformations import rename_columns, apply_partitions, update_cdc_timestamp, add_default_value_for_removed_col, rename_columns
# Mock databricks.sdk.runtime if not in a Databricks environment
try:
    from databricks.sdk.runtime import *
except ImportError:
    print("Databricks runtime not available. Mocking required modules.")
    mock_dbutils = mock.Mock()
    sys.modules['databricks.sdk.runtime'] = mock.Mock()
    sys.modules['dbruntime'] = mock.Mock()
    sys.modules['databricks'] = mock.Mock()

    # Mocking any specific methods you might call in your code
    mock_dbutils.jobs = mock.Mock()
    mock_dbutils.widgets = mock.Mock()
    mock_dbutils.notebook = mock.Mock()


def test_apply_partitions(spark):
    # Create a sample dataframe
    data = [
        Row(id=1, name="Alice", age=25),
        Row(id=2, name="Bob", age=30),
        Row(id=3, name="Charlie", age=35)
    ]
    df = spark.createDataFrame(data)
    
    # Define partitions (in this case, expressions for new columns)
    partitions = {
        "age_group": "CASE WHEN age < 30 THEN 'Young' ELSE 'Adult' END"
    }

    # Apply the function
    result_df = apply_partitions(df, partitions)
    
    # Check if the new partitioned column has been added correctly
    result = result_df.select("age_group").collect()

    assert result[0]['age_group'] == "Young"
    assert result[1]['age_group'] == "Adult"
    assert result[2]['age_group'] == "Adult"

def test_update_cdc_timestamp(spark):
    # Create a sample dataframe
    data = [
        Row(id=1, created_at=datetime(2024, 1, 1), updated_at=datetime(2024, 1, 10), cdc_timestamp=None),
        Row(id=2, created_at=datetime(2024, 1, 5), updated_at=datetime(2024, 1, 15), cdc_timestamp=datetime(2024, 1, 1)),
        Row(id=3, created_at=datetime(2024, 1, 8), updated_at=datetime(2024, 1, 12), cdc_timestamp=None)
    ]
    
    df = spark.createDataFrame(data)

    # Apply the function with a threshold of 5 days
    result_df = update_cdc_timestamp(df, time_diff_threshold=5)
    
    # Collect the results
    result = result_df.select("cdc_timestamp").collect()

    # The first and third rows should get updated with the greatest timestamp (updated_at)
    assert result[0]['cdc_timestamp'] == datetime(2024, 1, 10)
    assert result[2]['cdc_timestamp'] == datetime(2024, 1, 12)
    
    # The second row should retain its original cdc_timestamp because the difference is less than 5 days
    assert result[1]['cdc_timestamp'] == datetime(2024, 1, 1)




def test_add_default_value_for_removed_col(spark):
    data = [
        (1, None),
        (2, 2),
        (3, None)
    ]
    columns = ["id", "raw_data_index"]
    df = spark.createDataFrame(data, columns)

    default_value_for_removed_col = {
        'name': 'raw_data_index',
        'expr': 'cast(0 as int)' 
    }

    result_df = add_default_value_for_removed_col(df, default_value_for_removed_col)

    expected_data = [
        (1, 0),  
        (2, 2),  
        (3, 0) 
    ]
    expected_df = spark.createDataFrame(expected_data, columns)
    assert result_df.collect() == expected_df.collect()



def test_rename_columns(spark):
    data = [("Alice", 1), ("Bob", 2)]
    columns = ["name.first", "age"]
    df = spark.createDataFrame(data, columns)    
    df = df.transform(rename_columns)
    expected_columns = ["name_first", "age"]
    assert df.columns == expected_columns

