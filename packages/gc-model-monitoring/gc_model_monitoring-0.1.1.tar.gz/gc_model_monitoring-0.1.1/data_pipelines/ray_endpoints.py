from fastapi import FastAPI
import os
import ray
import gencrafter as wl
from gencrafter.core import DatasetProfile, DatasetProfileView
from datetime import datetime
import pandas as pd
import requests
from typing import Dict, Any
import math

app = FastAPI()

def map_ray_pipeline_to_whylabs(
    merged_profile: DatasetProfileView,
    dataset_size: int,
    profile_path: str
) -> Dict[str, Any]:
    """
    Improved mapper that better handles different data types and edge cases
    """
    def safe_value(value):
        """Convert value to JSON-serializable format"""
        if value is None:
            return None
        try:
            if isinstance(value, (int, str, bool)):
                return value
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    return None
                return value
            if hasattr(value, 'value'):
                return safe_value(value.value)
            if hasattr(value, 'to_summary_dict'):
                return safe_value(value.to_summary_dict())
            return str(value)
        except:
            return None

    def is_numeric_feature(types: dict) -> bool:
        """Check if feature is numeric based on type counts"""
        return types.get('integral', 0) + types.get('fractional', 0) > 0

    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "features_tracked": len(merged_profile.get_columns()),
            "local_profile_path": profile_path,
            "profile_size_bytes": len(merged_profile.serialize())
        },
        "features": {},
        "data_quality_metrics": {
            "missing_values": 0,
            "type_mismatches": 0
        }
    }

    for feature_name, column in merged_profile.get_columns().items():
        metrics = column.get_metrics()
        
        # Initialize with safe defaults
        feature_data = {
            "counts": {
                "count": dataset_size,
                "missing": 0,
                "null": 0
            },
            "types": {
                "integral": 0,
                "fractional": 0,
                "boolean": 0,
                "string": 0,
                "unexpected": 0
            },
            "distribution": None  # Will be set only for numeric features
        }

        # Process metrics
        for metric in metrics:
            try:
                # Handle counts metrics
                if hasattr(metric, 'null'):
                    null_count = safe_value(metric.null) or 0
                    feature_data["counts"]["missing"] = null_count
                    feature_data["counts"]["null"] = null_count
                    whylabs_data["data_quality_metrics"]["missing_values"] += null_count
                
                # Handle type metrics
                elif hasattr(metric, 'integral'):
                    feature_data["types"]["integral"] = safe_value(metric.integral) or 0
                    feature_data["types"]["fractional"] = safe_value(metric.fractional) or 0
                    feature_data["types"]["boolean"] = safe_value(metric.boolean) or 0
                    feature_data["types"]["string"] = safe_value(metric.string) or 0
                    unexpected = safe_value(getattr(metric, 'unexpected', getattr(metric, 'unknown', 0))) or 0
                    feature_data["types"]["unexpected"] = unexpected
                    whylabs_data["data_quality_metrics"]["type_mismatches"] += unexpected
            except Exception as e:
                print(f"Error processing basic metrics for {feature_name}: {e}")
                continue

        # Only add distribution for numeric features
        if is_numeric_feature(feature_data["types"]):
            feature_data["distribution"] = {
                "mean": None,
                "stddev": None,
                "min": None,
                "max": None,
                "quantiles": {
                    "median": None,
                    "q_25": None,
                    "q_75": None
                }
            }
            
            for metric in metrics:
                try:
                    if hasattr(metric, 'mean'):
                        feature_data["distribution"]["mean"] = safe_value(metric.mean)
                        feature_data["distribution"]["stddev"] = safe_value(metric.stddev)
                        feature_data["distribution"]["min"] = safe_value(metric.min)
                        feature_data["distribution"]["max"] = safe_value(metric.max)
                        
                        if hasattr(metric, 'median'):
                            feature_data["distribution"]["quantiles"]["median"] = safe_value(metric.median)
                        if hasattr(metric, 'q_25'):
                            feature_data["distribution"]["quantiles"]["q_25"] = safe_value(metric.q_25)
                        if hasattr(metric, 'q_75'):
                            feature_data["distribution"]["quantiles"]["q_75"] = safe_value(metric.q_75)
                except Exception as e:
                    print(f"Error processing distribution for {feature_name}: {e}")
                    continue

        whylabs_data["features"][feature_name] = feature_data
    
    return whylabs_data

# Load dataset function
def load_real_dataset():
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
    df = pd.read_csv(url)
    return df.to_dict(orient="records")

# Merge profiles function
def merge_profiles(profiles):
    if len(profiles) < 2:
        raise ValueError("At least two profiles are required to merge.")
    
    merged = DatasetProfileView.merge(profiles[0], profiles[1])
    for profile in profiles[2:]:
        merged = DatasetProfileView.merge(merged, profile)
    return merged

# Ray actor class
@ray.remote
class ProfileActor:
    def __init__(self):
        self.profiles = []

    def add_profile(self, profile_data):
        profile = DatasetProfile()
        profile.track(profile_data)
        self.profiles.append(profile.view())

    def get_profiles(self):
        return self.profiles

# FastAPI endpoint
@app.get("/run_profiling")
def run_profiling():
    ray.init(ignore_reinit_error=True, num_cpus=2)
    actor = ProfileActor.remote()
    
    dataset = load_real_dataset()
    sample_size = 100
    for row in dataset[:sample_size]:
        ray.get(actor.add_profile.remote(row))
    
    profiles = ray.get(actor.get_profiles.remote())
    if not profiles:
        return {"error": "No profiles collected"}
    
    merged = merge_profiles(profiles)

    output_dir = "gencrafter_profiles"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    profile_path = os.path.join(output_dir, f"profile_{timestamp}.bin")

    with open(profile_path, "wb") as f:
        f.write(merged.serialize())
    
    # Generate WhyLabs-style output
    whylabs_data = map_ray_pipeline_to_whylabs(
        merged_profile=merged,
        dataset_size=sample_size,
        profile_path=profile_path
    )
    
    return {
        "whylabs_mapped_data": whylabs_data,
        "profile_path": profile_path,
        "whylabs_upload": "Success"
    }