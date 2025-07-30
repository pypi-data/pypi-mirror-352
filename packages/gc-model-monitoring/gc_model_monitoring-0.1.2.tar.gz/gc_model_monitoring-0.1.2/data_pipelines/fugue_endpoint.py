import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
import gencrafter as why
from datetime import datetime
from typing import Dict, Any
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_extract(metric, default=None):
    """Safely extract metric values and handle NaN/inf values"""
    try:
        if metric is None:
            return default
        
        summary = metric.to_summary_dict()
        if isinstance(summary, dict):
            result = {}
            for k, v in summary.items():
                if hasattr(v, 'item'):
                    v = v.item()
                # Convert NaN/inf to None or a string representation
                if isinstance(v, float):
                    if np.isnan(v):
                        v = None
                    elif np.isinf(v):
                        v = None
                result[k] = v
            return result
        if hasattr(summary, 'item'):
            summary = summary.item()
        if isinstance(summary, float):
            if np.isnan(summary):
                return None
            elif np.isinf(summary):
                return None
        return summary
    except Exception as e:
        logger.debug(f"Metric extraction failed: {str(e)}")
        return default

def map_to_whylabs_format(profile_view, dataset_size: int) -> Dict[str, Any]:
    """Convert profile to WhyLabs format with proper metric extraction"""
    result = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "features_monitored": len(profile_view.get_columns()),
            "alert_status": "OK"
        },
        "features": {}
    }

    for column_name in profile_view.get_columns():
        col = profile_view.get_column(column_name)
        if col is None:
            continue
            
        # Extract all available metrics
        counts = safe_extract(col.get_metric("counts"), {})
        types = safe_extract(col.get_metric("types"), {})
        distribution = safe_extract(col.get_metric("distribution"), {})
        cardinality = safe_extract(col.get_metric("cardinality"), {})
        frequent_items = safe_extract(col.get_metric("frequent_items"), {})
        
        # Get the actual count if available
        actual_count = counts.get("count") if counts else dataset_size
        
        # Handle missing percentage calculation safely
        missing_percentage = None
        if actual_count and counts and "null" in counts:
            missing_percentage = counts["null"] / actual_count
        
        # Determine if the column is numeric or categorical
        is_numeric = distribution and "mean" in distribution
        
        feature_entry = {
            "counts": {
                "count": actual_count,
                "missing": counts.get("null", 0) if counts else 0,
                "null": counts.get("null", 0) if counts else 0,
                "distinct": cardinality.get("est") if cardinality else None
            },
            "types": {
                "type": str(types.get("type", "")),
                "inferred_type": str(types.get("inferred_type", ""))
            },
            "data_quality": {
                "missing_percentage": missing_percentage,
                "unexpected_values": 0
            }
        }
        
        # Add distribution only for numeric columns
        if is_numeric:
            feature_entry["distribution"] = {
                "mean": distribution.get("mean"),
                "stddev": distribution.get("stddev"),
                "min": distribution.get("min"),
                "max": distribution.get("max"),
                "quantiles": {
                    "q_01": distribution.get("q_01"),
                    "q_25": distribution.get("q_25"),
                    "q_50": distribution.get("median"),
                    "q_75": distribution.get("q_75"),
                    "q_99": distribution.get("q_99")
                }
            }
        
        # Add frequent items for categorical columns
        if frequent_items and "items" in frequent_items:
            feature_entry["frequent_items"] = [
                {"value": str(item["value"]), "count": item["estimate"]}
                for item in frequent_items["items"]
            ]
        
        result["features"][column_name] = feature_entry

    return result

def load_adult_dataset():
    """Load the UCI Adult dataset"""
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    columns = [
        "age", "workclass", "fnlwgt", "education", "education-num",
        "marital-status", "occupation", "relationship", "race",
        "sex", "capital-gain", "capital-loss", "hours-per-week",
        "native-country", "income"
    ]
    return pd.read_csv(url, names=columns, na_values="?", skipinitialspace=True)

@app.get("/profile")
def get_profile():
    """Endpoint to get profile data in WhyLabs format"""
    try:
        df = load_adult_dataset()
        profile_view = why.log(df).profile().view()
        profile_data = map_to_whylabs_format(profile_view, len(df))
        return JSONResponse(content=profile_data)
    except Exception as e:
        logger.error(f"Profile endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/upload")
def upload_to_whylabs():
    """Endpoint to upload profile to WhyLabs"""
    try:
        df = load_adult_dataset()
        profile = why.log(df)
       
        return {"status": "success", "message": "Profile uploaded to WhyLabs"}
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/full-process")
def full_process():
    """Complete process: profile + upload"""
    try:
        df = load_adult_dataset()
        profile = why.log(df)
        profile_view = profile.profile().view()
        profile_data = map_to_whylabs_format(profile_view, len(df))
        
  
        return JSONResponse(content={
            "status": "success",
            "profile_data": profile_data,
            "upload_status": "completed"
        })
    except Exception as e:
        logger.error(f"Full process failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))