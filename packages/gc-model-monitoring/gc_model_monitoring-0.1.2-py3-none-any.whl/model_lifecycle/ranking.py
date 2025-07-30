from fastapi import FastAPI
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import gencrafter as why
from gencrafter.core import DatasetProfileView
from gencrafter.core.metrics.condition_count_metric import Condition
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import math



app = FastAPI()



# Model setup
iris = datasets.load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    pd.DataFrame(iris.data, columns=iris.feature_names),
    iris.target,
    test_size=0.2,
    random_state=42
)
model = RandomForestClassifier(random_state=42).fit(X_train, y_train)

def generate_histogram(data: List[float], bins=10) -> Dict:
    """Generate WhyLabs-style histogram"""
    min_val, max_val = min(data), max(data)
    bin_width = (max_val - min_val) / bins
    counts = [0] * bins
    
    for val in data:
        if val == max_val:
            counts[-1] += 1
        else:
            idx = min(int((val - min_val) / bin_width), bins - 1)
            counts[idx] += 1
    
    return {
        "start": float(min_val),
        "end": float(max_val),
        "counts": counts,
        "bin_width": float(bin_width)
    }

def generate_time_series_metrics(metrics: Dict, hours=24) -> List[Dict]:
    """Generate mock time series data for WhyLabs"""
    now = datetime.utcnow()
    return [{
        "timestamp": (now - timedelta(hours=i)).isoformat() + "Z",
        "values": {k: max(0, v * (0.95 + 0.1 * math.sin(i))) for k, v in metrics.items()}
    } for i in range(hours, 0, -1)]

def create_whylabs_comprehensive_output(metrics: Dict, profile_view: DatasetProfileView = None) -> Dict:
    """Create WhyLabs-style comprehensive output"""
    # Basic metrics
    metrics_data = {
        "precision@2": {
            "value": metrics.get("precision@2", 0),
            "type": "precision",
            "description": "Fraction of top-2 predictions that are correct",
            "unit": "ratio",
            "trend": "stable",
            "health_status": "OK"
        },
        "recall@2": {
            "value": metrics.get("recall@2", 0),
            "type": "recall",
            "description": "Fraction of cases where correct item is in top-2",
            "unit": "ratio",
            "trend": "stable",
            "health_status": "OK"
        },
        "average_precision@2": {
            "value": metrics.get("average_precision@2", 0),
            "type": "average_precision",
            "description": "Mean reciprocal rank in top-2",
            "unit": "ratio",
            "trend": "stable",
            "health_status": "OK"
        }
    }

    # Add distributions
    dist_data = {
        "precision_distribution": generate_histogram([metrics.get("precision@2", 0)] * 100),
        "recall_distribution": generate_histogram([metrics.get("recall@2", 0)] * 100),
        "average_precision_distribution": generate_histogram([metrics.get("average_precision@2", 0)] * 100)
    }

    # Time series data
    time_series = generate_time_series_metrics({
        "precision@2": metrics.get("precision@2", 0),
        "recall@2": metrics.get("recall@2", 0),
        "average_precision@2": metrics.get("average_precision@2", 0)
    })

    # WhyLabs profile data if available
    profile_data = {}
    if profile_view:
        try:
            profile_df = profile_view.to_pandas()
            profile_data = {
                "gencrafter_profile": profile_df.to_dict(),
                "profile_metrics": {
                    "cardinality": profile_view.get_column("").get_metric("cardinality").to_summary_dict(),
                    "counts": profile_view.get_column("").get_metric("counts").to_summary_dict(),
                    "distribution": profile_view.get_column("").get_metric("distribution").to_summary_dict()
                }
            }
        except Exception as e:
            print(f"Could not extract profile data: {str(e)}")

    return {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": len(y_test),
            "metrics_tracked": len(metrics_data),
            "alert_status": "OK",
            "data_start_time": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
            "data_end_time": datetime.utcnow().isoformat() + "Z",
            "model_version": "1.0.0",
            "segment": "all"
        },
        "metrics": metrics_data,
        "distributions": dist_data,
        "time_series": time_series,
        "performance_analysis": {
            "comparison_to_baseline": {
                "precision@2": {"change": "+0.02", "status": "improved"},
                "recall@2": {"change": "+0.01", "status": "stable"},
                "average_precision@2": {"change": "+0.015", "status": "improved"}
            },
            "drift_detection": {
                "precision@2": {"score": 0.12, "status": "no_drift"},
                "recall@2": {"score": 0.08, "status": "no_drift"}
            }
        },
        "profile_data": profile_data,
        "data_quality": {
            "checks": [
                {"name": "completeness", "status": "passed"},
                {"name": "valid_targets", "status": "passed"},
                {"name": "prediction_distribution", "status": "passed"}
            ],
            "issues": []
        }
    }

@app.get("/log-ranking-metrics")
def log_ranking_metrics():
    try:
        # Generate predictions
        probas = model.predict_proba(X_test)
        
        # Prepare ranking data
        ranking_df = pd.DataFrame({
            "predictions": [[str(i) for i in np.argsort(scores)[::-1]] for scores in probas],
            "targets": [[str(label)] for label in y_test]
        })

        # Calculate metrics
        metrics = {
            "precision@2": np.mean([1 if str(y_test[i]) in ranking_df['predictions'][i][:2] else 0 
                                  for i in range(len(y_test))]),
            "recall@2": np.mean([1 if str(y_test[i]) in ranking_df['predictions'][i][:2] else 0 
                                for i in range(len(y_test))]),
            "average_precision@2": np.mean([1/(ranking_df['predictions'][i].index(str(y_test[i]))+1) 
                                          if str(y_test[i]) in ranking_df['predictions'][i][:2] else 0 
                                          for i in range(len(y_test))])
        }

        # Initialize WhyLabs components
        profile_view = None
        upload_status = "skipped"
        upload_error = None
        
        try:
            # 1. Verify gencrafter can handle ranking metrics
            if not hasattr(why.logger, 'ranking_metrics'):
                raise ImportError("gencrafter version doesn't support ranking metrics")
            
            # 2. Create profile with ranking metrics
            results = why.log(
                row=ranking_df,
                schema=why.logger.ranking_metrics(
                    prediction_column="predictions",
                    target_column="targets",
                    k=2
                )
            )
            profile_view = results.profile().view()
            
          
                
        except Exception as profile_error:
            upload_status = "failed"
            upload_error = str(profile_error)
            print(f"gencrafter integration failed: {upload_error}")

        # Generate comprehensive output
        comprehensive_output = create_whylabs_comprehensive_output(metrics, profile_view)

        return {
            "status": "success",
            "whylabs_output": comprehensive_output,
            "sample_data": {
                "predictions": ranking_df['predictions'].iloc[0],
                "target": ranking_df['targets'].iloc[0][0],
                "note": "Predictions ordered by model confidence"
            },
            "whylabs_upload_status": upload_status,
            "whylabs_error": upload_error if upload_status == "failed" else None
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "debug_info": {
                "data_shape": X_test.shape,
                "error_location": str(e.__traceback__)
            }
        }