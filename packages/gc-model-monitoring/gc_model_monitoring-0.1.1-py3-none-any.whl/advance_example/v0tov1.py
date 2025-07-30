from fastapi import FastAPI, Response
from gencrafter.core import DatasetProfile, DatasetProfileView

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any
import math
import json
import logging
import numpy as np

app = FastAPI()

# Load real e-commerce data and create a profile
def create_real_profile():
    # Using a real e-commerce dataset from Kaggle (public domain)
    url = "https://raw.githubusercontent.com/plotly/datasets/master/sample_ecommerce.csv"
    df = pd.read_csv(url)
    
    # Create a gencrafter profile from this data
    profile = DatasetProfile()
    profile.track(df)
    
    # Save to binary format (similar to original v0 format)
    profile_view = profile.view()
    PROFILE_FILE = "ecommerce_profile.bin"
    with open(PROFILE_FILE, "wb") as f:
        profile_view.serialize(f)
    
    return PROFILE_FILE

PROFILE_FILE = create_real_profile()

def safe_extract_value(obj, default=None):
    """Safely extract value from gencrafter metric components"""
    try:
        if hasattr(obj, 'value'):
            return obj.value
        if hasattr(obj, 'n'):
            return obj.n
        if hasattr(obj, 'count'):
            return obj.count
        return default
    except Exception:
        return default

def clean_metric_value(value):
    """Convert metric values to clean, JSON-safe representations"""
    try:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            if math.isnan(value) or math.isinf(value):
                return None
            return round(value, 3) if isinstance(value, float) else value
        if hasattr(value, '__dict__'):
            return str(value)
        return str(value)
    except Exception:
        return str(value)

def simplify_metrics(metrics):
    """Create simplified metric structure with complete error handling"""
    result = {}
    
    try:
        # Handle distribution metrics
        if 'distribution' in metrics:
            dist = metrics['distribution']
            clean_dist = {}
            for k in ['mean', 'stddev', 'max', 'min', 'median']:
                if k in dist:
                    clean_dist[k] = clean_metric_value(dist[k])
            # Only include relevant quantiles
            for q in ['q_25', 'q_75']:
                if q in dist:
                    clean_dist[q] = clean_metric_value(dist[q])
            if clean_dist:
                result['distribution'] = clean_dist
    
        # Simplify frequent items
        if 'frequent_items' in metrics:
            freq = metrics['frequent_items']
            if 'frequent_strings' in freq:
                try:
                    result['frequent_items'] = [
                        {'value': item['value'], 'count': int(safe_extract_value(item, {}).get('est', 0))}
                        for item in freq['frequent_strings']
                    ]
                except Exception:
                    pass
    
        # Simplify type counts
        if 'types' in metrics:
            try:
                result['types'] = {
                    k: int(safe_extract_value(v, 0)) 
                    for k, v in metrics['types'].items() 
                    if k in ['integral', 'fractional', 'string']
                }
            except Exception:
                pass
    
    except Exception as e:
        logging.error(f"Error simplifying metrics: {str(e)}")
    
    return result

def map_profile_to_whylabs(profile_view: DatasetProfileView) -> Dict[str, Any]:
    """Final robust mapping function with complete error handling"""
    result = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "dataset_name": "ecommerce_sample_data",
            "tags": {"source": "plotly_sample_data"},
            "total_features": 0,
            "total_observations": 0
        },
        "features": {},
        "model_performance": {"exists": False}
    }

    try:
        # Process columns
        columns = getattr(profile_view, "_columns", {})
        total_observations = 0
        
        for col_name, col_profile in columns.items():
            try:
                metrics = getattr(col_profile, "_metrics", {})
                
                # Get counts safely
                counts = metrics.get("counts")
                count = safe_extract_value(getattr(counts, "n", 0), 0)
                null_count = safe_extract_value(getattr(counts, "null", 0), 0)
                
                # Update summary stats
                if total_observations == 0 and count > 0:
                    total_observations = count
                
                # Serialize metrics
                metrics_summary = {}
                for metric_name, metric in metrics.items():
                    try:
                        if hasattr(metric, 'to_summary_dict'):
                            metrics_summary[metric_name] = metric.to_summary_dict()
                    except Exception:
                        pass
                
                result["features"][col_name] = {
                    "count": count,
                    "null_count": null_count,
                    "metrics": simplify_metrics(metrics_summary)
                }
                
            except Exception as e:
                logging.error(f"Error processing column {col_name}: {str(e)}")
                result["features"][col_name] = {
                    "error": f"Could not process column: {str(e)}"
                }

        # Update summary counts
        result["profile_summary"]["total_features"] = len(columns)
        result["profile_summary"]["total_observations"] = total_observations

        # Handle model performance metrics
        if hasattr(profile_view, "_model_performance_metrics"):
            model_metrics = profile_view._model_performance_metrics
            if model_metrics:
                result["model_performance"] = {
                    "exists": True,
                    "metrics": "Model performance metrics available"
                }
                
    except Exception as e:
        logging.error(f"Error mapping profile: {str(e)}")
        result["error"] = f"Profile processing error: {str(e)}"
    
    return result

@app.get("/profile_analysis")
def analyze_profile():
    try:
        # Load the profile we created
        with open(PROFILE_FILE, "rb") as f:
            view = DatasetProfileView.deserialize(f)
        
        profile_data = map_profile_to_whylabs(view)
        
        # Manual JSON serialization with error handling
        try:
            json_str = json.dumps(profile_data, default=lambda o: str(o))
            return Response(content=json_str, media_type="application/json")
        except Exception as e:
            return {"error": f"JSON serialization failed: {str(e)}"}
            
    except Exception as e:
        return {"error": str(e)}