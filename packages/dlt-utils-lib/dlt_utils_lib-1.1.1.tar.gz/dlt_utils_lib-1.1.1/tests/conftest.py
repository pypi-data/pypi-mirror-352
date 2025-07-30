import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope='session')
def spark():
    """Fixture for creating a Spark session."""
    spark = SparkSession.builder \
        .appName("PySpark Test") \
        .master("local[*]") \
        .getOrCreate()
    yield spark
    spark.stop()