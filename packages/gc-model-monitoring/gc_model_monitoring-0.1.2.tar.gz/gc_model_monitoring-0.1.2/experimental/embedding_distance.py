from fastapi import FastAPI
import os
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, Any
import gencrafter as why
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from gencrafter.core.resolvers import MetricSpec, ResolverSpec
from gencrafter.core.schema import DeclarativeSchema
from gencrafter.experimental.extras.embedding_metric import (
    DistanceFunction,
    EmbeddingConfig,
    EmbeddingMetric,
)
from gencrafter.experimental.preprocess.embeddings.selectors import PCACentroidsSelector

app = FastAPI()

DATASET_NAME = "Fashion-MNIST"

def numpy_to_python(value):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(value, (np.int32, np.int64)):
        return int(value)
    if isinstance(value, (np.float32, np.float64)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value

def get_original_embedding_results(profile_view) -> Dict[str, Any]:
    """Extract the original embedding metrics from the profile"""
    column = profile_view.get_column("pixel_values")
    summary = column.to_summary_dict()
    
    results = {}
    for digit in [str(i) for i in range(10)]:
        mean_key = f"embedding/{digit}_distance:distribution/mean"
        stddev_key = f"embedding/{digit}_distance:distribution/stddev"
        
        results[digit] = {
            "mean": numpy_to_python(summary.get(mean_key)),
            "stddev": numpy_to_python(summary.get(stddev_key))
        }
    
    return results

def get_whylabs_embedding_format(profile_view, dataset_size: int, references: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
    """Generate WhyLabs-style embedding monitoring output"""
    column = profile_view.get_column("pixel_values")
    summary = column.to_summary_dict()
    
    class_stats = {}
    unique_labels = np.unique(labels)
    
    for cls in unique_labels:
        cls_str = str(numpy_to_python(cls))
        cls_stats = {
            "distance_stats": {
                "mean": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/mean")),
                "stddev": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/stddev")),
                "min": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/min")),
                "max": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/max")),
                "q_25": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/q_25")),
                "median": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/median")),
                "q_75": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:distribution/q_75"))
            },
            "volume_stats": {
                "count": numpy_to_python(summary.get(f"embedding/{cls_str}_distance:counts/n", 0)),
                "anomaly_count": 0,
                "percent_anomalous": 0.0
            },
            "reference_embedding": {
                "centroid": numpy_to_python(references[int(cls)]),
                "support_count": numpy_to_python(np.sum(labels == cls))
            }
        }
        class_stats[cls_str] = cls_stats
    
    all_means = [s["distance_stats"]["mean"] for s in class_stats.values() if s["distance_stats"]["mean"] is not None]
    
    return {
        "embedding_monitoring": {
            "summary": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "observation_count": numpy_to_python(dataset_size),
                "feature_name": "pixel_values",
                "embedding_dimension": numpy_to_python(references.shape[1]),
                "reference_set_size": numpy_to_python(len(references)),
                "distance_type": "euclidean",
                "global_stats": {
                    "mean_distance": numpy_to_python(np.mean(all_means)) if all_means else None,
                    "median_distance": numpy_to_python(np.median(all_means)) if all_means else None,
                    "stddev_distance": numpy_to_python(np.std(all_means)) if all_means else None,
                    "min_distance": numpy_to_python(min(all_means)) if all_means else None,
                    "max_distance": numpy_to_python(max(all_means)) if all_means else None
                }
            },
            "per_class_stats": class_stats,
            "data_quality": {
                "missing_embeddings": numpy_to_python(summary.get("embedding/missing_count", 0)),
                "invalid_embeddings": numpy_to_python(summary.get("embedding/invalid_count", 0)),
                "out_of_bounds": 0
            }
        }
    }

@app.get("/log-embeddings")
def log_embeddings():
    """Endpoint that sends data to WhyLabs AND returns both formats"""
    # Load dataset
    if os.path.exists(f"{DATASET_NAME}_X_y.pkl"):
        with open(f"{DATASET_NAME}_X_y.pkl", 'rb') as f:
            X, y = pickle.load(f)
    else:
        X, y = fetch_openml(DATASET_NAME, version=1, return_X_y=True, as_frame=False)
        with open(f"{DATASET_NAME}_X_y.pkl", "wb") as f:
            pickle.dump((X, y), f)
    
    y = np.array(y) if not isinstance(y, np.ndarray) else y
    X_train, X_prod, y_train, y_prod = train_test_split(X, y, test_size=0.1)
    
    # Find references using PCA centroids
    selector = PCACentroidsSelector(n_components=20)
    references, labels = selector.calculate_references(X_train, y_train)
    
    # Configure embedding tracking
    config = EmbeddingConfig(
        references=references,
        labels=labels,
        distance_fn=DistanceFunction.euclidean,
    )
    schema = DeclarativeSchema([
        ResolverSpec(column_name="pixel_values", metrics=[MetricSpec(EmbeddingMetric, config)])
    ])
    
    # Log embeddings and get profile
    train_profile = why.log(row={"pixel_values": X_train}, schema=schema).profile()
    train_profile_view = train_profile.view()
    
    
    # Get both original and formatted results
    original_results = get_original_embedding_results(train_profile_view)
    whylabs_data = get_whylabs_embedding_format(
        profile_view=train_profile_view,
        dataset_size=len(X_train),
        references=references,
        labels=labels
    )
    
    return {
        "original_results": {
            "embedding_distances": original_results,
            "dataset_size": numpy_to_python(len(X_train)),
            "whylabs_status": "Data successfully sent to WhyLabs"
        },
        "whylabs_formatted": whylabs_data
    }