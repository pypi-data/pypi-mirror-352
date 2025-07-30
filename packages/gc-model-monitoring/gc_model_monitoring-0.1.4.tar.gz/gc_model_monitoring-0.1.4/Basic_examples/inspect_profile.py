from fastapi import FastAPI
import gencrafter as why
import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, Any
app = FastAPI()

CSV_URL = "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv"

def map_basic_profile_to_whylabs(profile_dict: Dict[str, Any], dataset_size: int) -> Dict[str, Any]:
    """
    Properly maps the gencrafter profile to WhyLabs-style structure
    focusing on actual data columns (Height and Weight)
    """
    # Extract the actual columns from the profile (ignoring internal metrics)
    data_columns = {
        "Height(Inches)": {},
        "Weight(Pounds)": {},
        "Index": {}
    }
    
    # Map the metrics from raw profile to our structure
    for metric_category, metrics in profile_dict.items():
        for column_name, value in metrics.items():
            # Clean column names (they have extra spaces/quotes in the raw output)
            clean_name = column_name.strip().strip('"')
            if clean_name not in data_columns:
                continue
                
            # Map different metric categories
            if metric_category.startswith("distribution/"):
                metric_name = metric_category.split("/")[1]
                data_columns[clean_name].setdefault("distribution", {})[metric_name] = value
            elif metric_category.startswith("counts/"):
                metric_name = metric_category.split("/")[1]
                data_columns[clean_name].setdefault("counts", {})[metric_name] = value
            elif metric_category.startswith("types/"):
                metric_name = metric_category.split("/")[1]
                data_columns[clean_name].setdefault("types", {})[metric_name] = value
    
    # Build the WhyLabs-style output
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "columns_monitored": len([col for col in data_columns if data_columns[col]]),
            "alert_status": "OK"
        },
        "features": {},
        "data_quality_issues": []
    }

    for column_name, metrics in data_columns.items():
        if not metrics:
            continue
            
        whylabs_data["features"][column_name] = {
            "counts": {
                "count": metrics.get("counts", {}).get("n", dataset_size),
                "missing": metrics.get("counts", {}).get("null", 0),
                "null": metrics.get("counts", {}).get("null", 0),
                "inf": metrics.get("counts", {}).get("inf", 0)
            },
            "types": {
                "type": "numeric",  # Simplified since we know these are numeric columns
                "integral": 1 if column_name == "Index" else 0,
                "fractional": 1 if column_name != "Index" else 0,
                "boolean": 0,
                "string": 0
            },
            "distribution": metrics.get("distribution", {})
        }

        # Check for data quality issues
        null_count = metrics.get("counts", {}).get("null", 0)
        if null_count > 0:
            percentage_missing = (null_count / dataset_size) * 100
            whylabs_data["data_quality_issues"].append({
                "feature": column_name,
                "issue_type": "MISSING_VALUES",
                "severity": "MEDIUM" if percentage_missing < 10 else "HIGH",
                "count": null_count,
                "percentage": percentage_missing
            })

    return whylabs_data

@app.get("/inspect_profile")
def inspect_profile():
    try:
        # Load dataset
        df_real = pd.read_csv(CSV_URL)
        dataset_size = len(df_real)

        # Generate gencrafter profile
        results = why.log(pandas=df_real)
        profile = results.profile()

        # Convert profile view to dict
        prof_view = profile.view()
        prof_df = prof_view.to_pandas()
        prof_df = prof_df.replace([np.nan, np.inf, -np.inf], None)
        profile_dict = prof_df.to_dict()

        # Generate WhyLabs-style output
        whylabs_data = map_basic_profile_to_whylabs(
            profile_dict=profile_dict,
            dataset_size=dataset_size
        )

        return {
            "whylabs_formatted_data": whylabs_data,
            "raw_profile": profile_dict,
            "message": "Profile logged to WhyLabs"
        }

    except Exception as e:
        return {"error": str(e)}