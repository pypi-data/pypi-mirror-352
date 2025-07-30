# drift_mapper.py
from datetime import datetime
from typing import Dict, Any
import numpy as np
from gencrafter.core import DatasetProfileView

def map_drift_to_whylabs(
    target_view: DatasetProfileView,
    reference_view: DatasetProfileView,
    drift_scores: Dict[str, Any],
    dataset_size: int
) -> Dict[str, Any]:
    """
    Updated mapper that correctly handles drift detection results
    """
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "drifted_features": [],
            "global_drift_score": 0,
            "alert_status": "OK"
        },
        "features": {},
        "drift_analysis": {
            "reference_profile_id": "reference_profile",
            "comparison_window": "snapshot",
            "feature_drift_scores": {}
        },
        "data_quality_issues": []
    }

    drifted_features = []
    max_drift_score = 0
    
    for feature_name, scores in drift_scores.items():
        if not isinstance(scores, dict) or scores is None:
            continue
            
        # Determine drift status
        drift_category = scores.get("drift_category", "NO_DRIFT")
        is_drifted = drift_category == "DRIFT"
        is_possible_drift = drift_category == "POSSIBLE_DRIFT"
        
        # Calculate drift score (using p-value inverted)
        p_value = scores.get("pvalue", 1.0)
        drift_score = 1 - min(max(p_value, 0), 1)  # Convert p-value to drift score
        
        # Update max drift score
        if is_drifted and drift_score > max_drift_score:
            max_drift_score = drift_score
        
        # Set confidence level
        confidence = "HIGH" if is_drifted else ("MEDIUM" if is_possible_drift else "LOW")
        
        # Feature entry
        whylabs_data["features"][feature_name] = {
            "drift_metrics": {
                "p_value": p_value,
                "algorithm": scores.get("algorithm"),
                "statistic": scores.get("statistic"),
                "confidence": confidence,
                "thresholds": scores.get("thresholds")
            },
            "status": "DRIFTED" if is_drifted else ("POSSIBLE_DRIFT" if is_possible_drift else "STABLE")
        }
        
        whylabs_data["drift_analysis"]["feature_drift_scores"][feature_name] = drift_score
        
        if is_drifted:
            drifted_features.append(feature_name)
            whylabs_data["data_quality_issues"].append({
                "feature": feature_name,
                "issue_type": "DATA_DRIFT",
                "severity": "HIGH",
                "drift_score": drift_score,
                "algorithm": scores.get("algorithm"),
                "p_value": p_value
            })
    
    # Update summary
    whylabs_data["profile_summary"]["drifted_features"] = drifted_features
    whylabs_data["profile_summary"]["global_drift_score"] = max_drift_score
    whylabs_data["profile_summary"]["alert_status"] = "WARNING" if drifted_features else "OK"
    
    return whylabs_data

def clean_json(obj):
    """Handle NaN/Infinity values"""
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(v) for v in obj]
    elif isinstance(obj, float):
        return None if np.isnan(obj) or np.isinf(obj) else obj
    return obj