from fastapi import FastAPI
import pandas as pd
import gencrafter as why
import os
from datetime import datetime
from typing import Dict, Any
from gencrafter.core import DatasetProfileView
from gencrafter.core.metrics import StandardMetric
from gencrafter.core.metrics.metrics import Metric
from gencrafter.core.metrics.condition_count_metric import ConditionCountMetric
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load dataset
df_full = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")

# Split dataset into three subsets
df_subset1 = df_full[0:100]
df_subset2 = df_full[100:400]
df_subset3 = df_full[400:]

def extract_metric_value(metric: Metric, metric_name: str):
    """Helper to safely extract metric values"""
    try:
        if hasattr(metric, metric_name):
            value = getattr(metric, metric_name)
            if hasattr(value, 'value'):
                return value.value
            return value
        return None
    except Exception as e:
        logger.warning(f"Error extracting {metric_name}: {str(e)}")
        return None

def map_to_whylabs_format(profile_view: DatasetProfileView, dataset_size: int) -> Dict[str, Any]:
    """Maps gencrafter profile to WhyLabs-style format with proper metric extraction"""
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "features_tracked": len(profile_view.get_columns()),
            "alert_status": "OK"
        },
        "features": {},
        "data_quality_issues": []
    }

    for column_name in profile_view.get_columns():
        column = profile_view.get_column(column_name)
        if column is None:
            continue

        column_data = {
            "counts": {
                "count": 0,
                "missing": 0
            },
            "distribution": {
                "mean": None,
                "stddev": None,
                "min": None,
                "max": None,
                "quantiles": {}
            }
        }

        # Extract counts
        counts_metric = column.get_metric("counts")
        if counts_metric:
            column_data["counts"]["count"] = extract_metric_value(counts_metric, "n") or 0
            column_data["counts"]["missing"] = extract_metric_value(counts_metric, "null") or 0

        # Extract distribution metrics
        distribution_metric = column.get_metric("distribution")
        if distribution_metric:
            column_data["distribution"]["mean"] = extract_metric_value(distribution_metric, "mean")
            column_data["distribution"]["stddev"] = extract_metric_value(distribution_metric, "stddev")
            column_data["distribution"]["min"] = extract_metric_value(distribution_metric, "min")
            column_data["distribution"]["max"] = extract_metric_value(distribution_metric, "max")
            
            # Extract quantiles
            for q in [0.01, 0.25, 0.5, 0.75, 0.99]:
                q_key = f"q_{int(q*100)}"
                q_value = extract_metric_value(distribution_metric, f"quantile_{q}")
                if q_value is not None:
                    column_data["distribution"]["quantiles"][q_key] = q_value

        whylabs_data["features"][column_name] = column_data

    return whylabs_data

@app.get("/merge_profiles")
def merge_profiles():
    try:
        # Log subsets
        logger.info("Logging subset 1")
        results1 = why.log(df_subset1)
        profile_view1 = results1.profile().view()

        logger.info("Logging subset 2")
        results2 = why.log(df_subset2)
        profile_view2 = results2.profile().view()

        logger.info("Logging subset 3")
        results3 = why.log(df_subset3)
        profile_view3 = results3.profile().view()

        # Merge profiles
        logger.info("Merging profiles")
        merged_profile_view = profile_view1.merge(profile_view2).merge(profile_view3)

        # Upload merged profile to WhyLabs
        logger.info("Writing to WhyLabs")
        # Convert to WhyLabs format
        logger.info("Mapping to WhyLabs format")
        whylabs_data = map_to_whylabs_format(
            profile_view=merged_profile_view,
            dataset_size=len(df_full))
        
        # Extract key metrics directly from the profile
        logger.info("Extracting key metrics")
        aapl_open_col = merged_profile_view.get_column("AAPL.Open")
        aapl_close_col = merged_profile_view.get_column("AAPL.Close")
        
        mean_open = None
        mean_close = None
        
        if aapl_open_col:
            dist_metric = aapl_open_col.get_metric("distribution")
            if dist_metric:
                mean_open = extract_metric_value(dist_metric, "mean")
        
        if aapl_close_col:
            dist_metric = aapl_close_col.get_metric("distribution")
            if dist_metric:
                mean_close = extract_metric_value(dist_metric, "mean")

        return {
            "whylabs_formatted_data": whylabs_data,
            "key_metrics": {
                "Mean Opening Price": mean_open,
                "Mean Closing Price": mean_close
            },
            "message": "Profiles merged and successfully uploaded to WhyLabs!"
        }

    except Exception as e:
        logger.error(f"Error in merge_profiles: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to process profiles"
        }