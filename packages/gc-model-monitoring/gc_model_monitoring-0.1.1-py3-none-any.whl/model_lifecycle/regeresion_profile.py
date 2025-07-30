
import warnings
import math
from fastapi import FastAPI
import requests
import pandas as pd
import gencrafter as why
from datetime import datetime, timezone
from gencrafter.core.segmentation_partition import segment_on_column
from gencrafter.core.schema import DatasetSchema
import os
import json
from typing import Dict, Any
import os
warnings.simplefilter(action="ignore", category=FutureWarning)

app = FastAPI()



class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        return super().default(obj)

def clean_json(data):
    """Recursively clean data for JSON serialization"""
    if isinstance(data, dict):
        return {k: clean_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json(item) for item in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    return data

def format_whylabs_output(profile_view) -> Dict[str, Any]:
    """Format gencrafter profile to WhyLabs-style dashboard output"""
    try:
        # Initialize WhyLabs-style output structure
        whylabs_output = {
            "summary": {},
            "features": {},
            "metrics": {}
        }
        
        # Get all columns from the profile
        columns = profile_view.get_columns()
        
        # Add summary metrics
        summary_metrics = {}
        if "" in profile_view._columns:  # Check for root column
            root_column = profile_view._columns[""]
            if hasattr(root_column, "_metrics"):
                if "counts" in root_column._metrics:
                    counts = root_column._metrics["counts"].to_summary_dict()
                    summary_metrics.update({
                        "total_count": clean_json(counts.get("n", 0)),
                        "missing_count": clean_json(counts.get("null", 0)),
                    })
                if "types" in root_column._metrics:
                    types = root_column._metrics["types"].to_summary_dict()
                    summary_metrics.update({
                        "completeness": clean_json(types.get("type/completeness", 0)),
                        "inferred_type": str(types.get("type/inferred_type", "unknown"))
                    })
        
        whylabs_output["summary"] = summary_metrics
        
        # Add feature-level metrics
        for feature, column_view in columns.items():
            if feature == "":  # Skip root column
                continue
                
            feature_metrics = {}
            metrics = column_view._metrics
            
            # Distribution metrics
            if "distribution" in metrics:
                dist = metrics["distribution"].to_summary_dict()
                feature_metrics["distribution"] = {
                    "mean": clean_json(dist.get("mean")),
                    "stddev": clean_json(dist.get("stddev")),
                    "min": clean_json(dist.get("min")),
                    "max": clean_json(dist.get("max")),
                    "quantiles": {
                        "q25": clean_json(dist.get("q_25")),
                        "q50": clean_json(dist.get("median")),
                        "q75": clean_json(dist.get("q_75"))
                    }
                }
            
            # Type metrics
            if "types" in metrics:
                type_metrics = metrics["types"].to_summary_dict()
                feature_metrics["types"] = {
                    "type": str(type_metrics.get("type/inferred_type", "unknown")),
                    "completeness": clean_json(type_metrics.get("type/completeness", 0))
                }
            
            # Counts
            if "counts" in metrics:
                count_metrics = metrics["counts"].to_summary_dict()
                feature_metrics["counts"] = {
                    "count": clean_json(count_metrics.get("n", 0)),
                    "missing_count": clean_json(count_metrics.get("null", 0))
                }
            
            whylabs_output["features"][feature] = feature_metrics
        
        # Add regression metrics if available
        if "" in profile_view._columns and "regression_score" in profile_view._columns[""]._metrics:
            regression_metrics = profile_view._columns[""]._metrics["regression_score"].to_summary_dict()
            whylabs_output["metrics"]["regression"] = {
                "mean_absolute_error": clean_json(regression_metrics.get("mean_absolute_error")),
                "mean_squared_error": clean_json(regression_metrics.get("mean_squared_error")),
                "root_mean_squared_error": clean_json(regression_metrics.get("root_mean_squared_error"))
            }
        
        return whylabs_output
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate_regression_profile")  # Fixed the endpoint name
def generate_regression_profile():
    try:
        # Fetch historical weather data
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        response = requests.get(url, params=params)
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame({
            "date": pd.to_datetime(data["daily"]["time"]),
            "temperature": data["daily"]["temperature_2m_max"],
            "temperature_min": data["daily"]["temperature_2m_min"],
            "precipitation": data["daily"]["precipitation_sum"]
        })

        # Assign climate types
        def classify_climate(temp):
            if temp < 10:
                return "dry"
            elif temp < 20:
                return "mild temperate"
            elif temp < 30:
                return "tropical"
            else:
                return "hot desert"

        df["meta_climate"] = df["temperature"].apply(classify_climate)
        df["meta_latitude"] = 37.7749
        df["meta_longitude"] = -122.4194
        df["prediction_temperature"] = df["temperature"] - (df["temperature"] * 0.1)
        df.set_index("date", inplace=True)

        # Segment the schema
        segment_column = "meta_climate"
        segmented_schema = DatasetSchema(segments=segment_on_column(segment_column))

        
        # Validate WhyLabs config
        return {
                "status": "error",
                "message": "WhyLabs configuration incomplete",
                "required_env_vars": {
                    "WHYLABS_API_KEY": "Set to your API key",
                    "WHYLABS_DEFAULT_ORG_ID": "Set to your organization ID",
                    "WHYLABS_DEFAULT_DATASET_ID": "Set to your dataset ID"
                }
            }
        # Process daily batches
        daily_batches = [df.loc[[date]] for date in df.index]
        results_summary = []

        for batch in daily_batches[:5]:  # Limiting to 5 days for demonstration
            dataset_timestamp = batch.index[0].replace(tzinfo=timezone.utc)

            results = why.log_regression_metrics(
                batch,
                target_column="temperature",
                prediction_column="prediction_temperature",
                schema=segmented_schema,
                log_full_data=True
            )

            profile = results.profile()
            profile.set_dataset_timestamp(dataset_timestamp)
            
            
            # Get profile view
            profile_view = results.view()
            
            # Get raw gencrafter output with cleaned data
            gencrafter_output = clean_json(profile_view.to_pandas().to_dict())
            
            # Get formatted WhyLabs output
            whylabs_output = format_whylabs_output(profile_view)
           
            results_summary.append(clean_json({
                "date": str(dataset_timestamp),
                "temperature": batch["temperature"].values[0],
                "prediction_temperature": batch["prediction_temperature"].values[0],
                "climate": batch["meta_climate"].values[0],
                "gencrafter_output": gencrafter_output,
                "whylabs_output": whylabs_output
            }))

        return {
            "status": "success", 
            "data": results_summary,
          
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": str(e.__traceback__)
        }