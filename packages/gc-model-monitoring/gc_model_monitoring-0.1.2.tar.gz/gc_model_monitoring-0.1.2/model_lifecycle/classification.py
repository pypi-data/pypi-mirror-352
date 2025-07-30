from fastapi import FastAPI, HTTPException
import pandas as pd
import gencrafter as why
import traceback
from gencrafter.core import DatasetSchema
from gencrafter.core.view.dataset_profile_view import DatasetProfileView
import os
from datetime import datetime
from typing import Dict, Any, Union
import json

app = FastAPI()

def fetch_real_dataset() -> pd.DataFrame:
    """Fetches the adult income dataset"""
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    columns = [
        "age", "workclass", "fnlwgt", "education", "educational-num", "marital-status",
        "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss",
        "hours-per-week", "native-country", "income"
    ]
    df = pd.read_csv(url, names=columns, na_values=" ?", skipinitialspace=True)
    df.dropna(inplace=True)
    return df

def serialize_metric_value(value: Any) -> Union[int, float, str, dict, list, None]:
    """Recursively serialize gencrafter metric values"""
    if value is None:
        return None
    if isinstance(value, (int, float, str)):
        return value
    if hasattr(value, 'value'):
        return serialize_metric_value(value.value)
    if hasattr(value, '__dict__'):
        return {k: serialize_metric_value(v) for k, v in vars(value).items() if not k.startswith('_')}
    if isinstance(value, (list, tuple)):
        return [serialize_metric_value(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize_metric_value(v) for k, v in value.items()}
    return str(value)

def get_whylabs_formatted_data(profile_view: DatasetProfileView, dataset_size: int) -> Dict[str, Any]:
    """Converts gencrafter profile to WhyLabs-style format"""
    def safe_get_metric(metric_obj, attr_name, default=None):
        """Safely extract metric attributes"""
        if not hasattr(metric_obj, attr_name):
            return default
        attr = getattr(metric_obj, attr_name)
        return serialize_metric_value(attr)

    features = {}
    for col_name in profile_view.get_columns():
        col_profile = profile_view.get_column(col_name)
        if not col_profile:
            continue

        # Initialize feature entry
        features[col_name] = {
            "counts": {
                "count": dataset_size,
                "missing": 0,
                "null": 0
            },
            "distribution": {
                "mean": None,
                "stddev": None,
                "min": None,
                "max": None,
                "quantiles": {
                    "q_25": None,
                    "q_50": None,
                    "q_75": None
                },
                "frequent_items": []
            }
        }

        # Extract counts metrics
        counts_metric = col_profile._metrics.get("counts")
        if counts_metric:
            features[col_name]["counts"]["missing"] = safe_get_metric(counts_metric, 'null', 0)
            features[col_name]["counts"]["null"] = safe_get_metric(counts_metric, 'null', 0)

        # Extract distribution metrics
        dist_metric = col_profile._metrics.get("distribution")
        if dist_metric:
            features[col_name]["distribution"].update({
                "mean": safe_get_metric(dist_metric, 'mean'),
                "stddev": safe_get_metric(dist_metric, 'stddev'),
                "min": safe_get_metric(dist_metric, 'min'),
                "max": safe_get_metric(dist_metric, 'max'),
                "quantiles": {
                    "q_25": safe_get_metric(dist_metric, 'q_25'),
                    "q_50": safe_get_metric(dist_metric, 'median'),
                    "q_75": safe_get_metric(dist_metric, 'q_75')
                }
            })

        # Extract frequent items
        freq_items = col_profile._metrics.get("frequent_items")
        if freq_items and hasattr(freq_items, 'items'):
            features[col_name]["distribution"]["frequent_items"] = [
                {"value": str(item.value), "count": int(item.estimate)}
                for item in freq_items.items[:5]  # Top 5 frequent items
                if hasattr(item, 'value') and hasattr(item, 'estimate')
            ]

    return {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "num_features": len(features),
            "alert_status": "OK"
        },
        "features": features
    }

@app.post("/log_classification_metrics/")
def log_classification_metrics_api():
    try:
        df = fetch_real_dataset()
        schema = DatasetSchema()
        profile = why.log(df, schema=schema).profile()
        profile_view = profile.view()

        # Get original gencrafter profile data (serialized properly)
        original_profile = {
            "columns": list(profile_view.get_columns().keys()),
            "metrics": {
                col: {
                    metric: serialize_metric_value(metric_obj)
                    for metric, metric_obj in col_profile._metrics.items()
                }
                for col, col_profile in profile_view.get_columns().items()
            }
        }

        # Get WhyLabs-formatted data
        whylabs_data = get_whylabs_formatted_data(profile_view, len(df))


        return {
            "message": "Metrics logged successfully",
            "original_gencrafter_profile": original_profile,
            "whylabs_formatted_data": whylabs_data
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Classification Monitoring API"}