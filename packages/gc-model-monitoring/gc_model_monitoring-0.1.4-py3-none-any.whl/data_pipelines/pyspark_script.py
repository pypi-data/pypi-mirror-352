from fastapi import FastAPI
from pyspark.sql import SparkSession
from pyspark.sql.functions import mean
from pyspark import SparkFiles
from gencrafter.api.pyspark.experimental import (
    collect_column_profile_views,
    collect_dataset_profile_view,
)
import os
import json

app = FastAPI()

# Initialize Spark Session
spark = SparkSession.builder.appName("gencrafter-fastapi").getOrCreate()
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

# Load Titanic dataset
data_url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
spark.sparkContext.addFile(data_url)
spark_dataframe = spark.read.option("inferSchema", "true").csv(SparkFiles.get("titanic.csv"), header=True)

# Collect profiles
column_views_dict = collect_column_profile_views(spark_dataframe)
dataset_profile_view = collect_dataset_profile_view(input_df=spark_dataframe)

# Function to map data to the structured format
def map_to_structured_format():
    # Dataset metadata
    dataset_metadata = {
        "dataset_name": "titanic",
        "timestamp": "2025-03-25T12:00:00Z",
        "schema_version": "1.0"
    }

    # Data quality
    data_quality = {}
    missing_values = {}
    null_counts = {}
    
    for column, view in column_views_dict.items():
        missing_values[column] = view.get_metric("missing_value").n.value if view.get_metric("missing_value") else 0
        null_counts[column] = spark_dataframe.filter(spark_dataframe[column].isNull()).count()
    
    data_quality["missing_values"] = missing_values
    data_quality["null_counts"] = null_counts

    # Statistics
    statistics = {}
    for column in spark_dataframe.columns:
        stats = spark_dataframe.describe([column]).toPandas()
        statistics[column] = {
            "mean": float(stats[stats["summary"] == "mean"][column].values[0]),
            "median": float(stats[stats["summary"] == "50%"][column].values[0]),
            "std_dev": float(stats[stats["summary"] == "stddev"][column].values[0]),
            "min": float(stats[stats["summary"] == "min"][column].values[0]),
            "max": float(stats[stats["summary"] == "max"][column].values[0]),
        }

    # Drift detection (example: random drift score)
    drift_detection = {}
    for column in spark_dataframe.columns:
        drift_detection[column] = {
            "drift_score": 0.15,  # This can be calculated based on your drift detection logic
            "status": "no_drift"  # Placeholder: logic to detect drift can be added
        }

    # Bias analysis (example: label distribution)
    bias_analysis = {
        "label_distribution": {
            "Survived_0": 0.62,
            "Survived_1": 0.38
        },
        "fairness_metrics": {
            "demographic_parity": 0.85,
            "equal_opportunity": 0.77
        }
    }

    # Anomalies (example: simple outlier count)
    anomalies = {}
    for column in spark_dataframe.columns:
        anomalies[column] = {
            "outlier_count": 3,  # Placeholder: actual logic for anomaly detection needed
            "trend_deviation": 0.1  # Placeholder: actual logic for trend deviation needed
        }

    # Final mapped output
    mapped_data = {
        "dataset_metadata": dataset_metadata,
        "data_quality": data_quality,
        "statistics": statistics,
        "drift_detection": drift_detection,
        "bias_analysis": bias_analysis,
        "anomalies": anomalies
    }

    return mapped_data

@app.get("/column-stats/{column_name}")
def get_column_stats(column_name: str):
    """Retrieve column statistics (count, mean, distribution)."""
    if column_name not in column_views_dict:
        return {"error": "Column not found"}
    
    count = column_views_dict[column_name].get_metric("counts").n.value
    mean_value = column_views_dict[column_name].get_metric("distribution").mean.value
    return {"column": column_name, "count": count, "mean": mean_value}

@app.get("/dataset-profile")
def get_dataset_profile():
    """Return dataset profile as JSON."""
    mapped_data = map_to_structured_format()  # Get the mapped data
    return mapped_data

@app.get("/mean/{column_name}")
def compute_mean(column_name: str):
    """Compute mean of a column using Spark."""
    if column_name not in spark_dataframe.columns:
        return {"error": "Column not found"}
    
    mean_value = spark_dataframe.select(mean(column_name)).collect()[0][0]
    return {"column": column_name, "mean": mean_value}


@app.get("/health")
def health_check():
    return {"status": "FastAPI gencrafter Service is running"}
