
from fastapi import FastAPI
import pandas as pd
import gencrafter as why
from gencrafter.core.schema import ColumnSchema, DatasetSchema
from gencrafter.core.metrics.unicode_range import UnicodeRangeMetric
from gencrafter.core.resolvers import Resolver
from gencrafter.core.datatypes import DataType
from gencrafter.core.metrics import Metric, MetricConfig
from gencrafter.core.relations import Predicate
from gencrafter.core.metrics.condition_count_metric import Condition
from gencrafter.core.resolvers import STANDARD_RESOLVER
from gencrafter.core.specialized_resolvers import ConditionCountMetricSpec
from gencrafter.core.schema import DeclarativeSchema
from gencrafter.core.constraints.factories import condition_meets, condition_never_meets, condition_count_below
from gencrafter.core.constraints import ConstraintsBuilder
from datetime import datetime
from typing import Dict, Any
import numpy as np
import os

app = FastAPI()

# ==============================================
# 1. COMMON SETUP (IRIS DATASET + WHYLABS WRITER)
# ==============================================

# Load Iris dataset
iris_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
column_names = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
try:
    iris_df = pd.read_csv(iris_url, names=column_names)
except:
    iris_df = pd.DataFrame(columns=column_names)  # Fallback empty DataFrame

# ==============================================
# 2. MAPPING FUNCTIONS (gencrafter → WHYLABS FORMAT)
# ==============================================

def map_tracking_profile_to_whylabs(profile_view_df: Dict[str, Any], dataset_size: int) -> Dict[str, Any]:
    """Maps tracking profile to WhyLabs format"""
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "features_tracked": len(profile_view_df),
            "alert_status": "OK"
        },
        "features": {},
        "data_quality_metrics": {}
    }

    for feature_name, metrics in profile_view_df.items():
        feature_data = {}
        
        # Standard metrics
        if 'counts/n' in metrics:
            feature_data["counts"] = {
                "count": metrics['counts/n'],
                "missing": metrics.get('counts/null', 0),
                "inf": metrics.get('counts/inf', 0)
            }
        
        # Distribution metrics
        if 'distribution/mean' in metrics:
            feature_data["distribution"] = {
                "mean": metrics['distribution/mean'],
                "stddev": metrics['distribution/stddev'],
                "min": metrics['distribution/min'],
                "max": metrics['distribution/max'],
                "quantiles": {
                    "q_25": metrics.get('distribution/q_25'),
                    "q_50": metrics.get('distribution/median'),
                    "q_75": metrics.get('distribution/q_75')
                }
            }
        
        # Type metrics
        if 'types/integral' in metrics:
            feature_data["types"] = {
                "integral": metrics['types/integral'],
                "fractional": metrics['types/fractional'],
                "boolean": metrics.get('types/boolean', 0),
                "string": metrics.get('types/string', 0)
            }
        
        if feature_data:
            whylabs_data["features"][feature_name] = feature_data
            whylabs_data["data_quality_metrics"][feature_name] = {
                "completeness": 1 - metrics.get('counts/null', 0) / metrics['counts/n'] if metrics['counts/n'] > 0 else 1.0,
                "uniqueness": metrics.get('cardinality/est', 0) / metrics['counts/n'] if metrics['counts/n'] > 0 else 0
            }

    return whylabs_data

def map_constraints_to_whylabs(constraints_report, dataset_size: int) -> Dict[str, Any]:
    """Maps constraints to WhyLabs format"""
    report_data = {
        "constraints": [],
        "summary": {
            "total": len(constraints_report),
            "passed": sum(1 for r in constraints_report if r.passed),
            "failed": sum(1 for r in constraints_report if not r.passed)
        }
    }
    
    for constraint in constraints_report:
        feature = constraint.name.split()[0] if constraint.name else "unknown"
        report_data["constraints"].append({
            "feature": feature,
            "name": constraint.name,
            "status": "PASS" if constraint.passed else "FAIL",
            "metric": getattr(constraint, 'metric', None)
        })
    
    return {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "constraints_evaluated": report_data["summary"]["total"],
            "constraints_passed": report_data["summary"]["passed"],
            "alert_status": "OK" if report_data["summary"]["failed"] == 0 else "WARNING"
        },
        "constraints_report": report_data
    }

# ==============================================
# 3. API ENDPOINTS
# ==============================================

@app.get("/track")
def track_data():
    """Tracking endpoint with custom unicode metrics"""
    # Custom schema for unicode tracking
    class UnicodeResolver(Resolver):
        def resolve(self, name: str, why_type: DataType, column_schema: ColumnSchema) -> Dict[str, Metric]:
            return {UnicodeRangeMetric.get_namespace(): UnicodeRangeMetric.zero(column_schema.cfg)}
    
    config = MetricConfig(unicode_ranges={"digits": (48, 57), "alpha": (97, 122)})
    schema = DatasetSchema(resolvers=UnicodeResolver(), default_configs=config)
    
    # Profile and upload
    profile = why.log(iris_df, schema=schema).profile()
    
    # Convert and map
    profile_view = profile.view()
    profile_dict = profile_view.to_pandas().replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict()
    
    return {
        "status": "success",
        "data": map_tracking_profile_to_whylabs(profile_dict, len(iris_df))
    }

@app.get("/validate")
def validate_data():
    """Validation endpoint with constraints"""
    # Define constraints
    def is_positive(x): return x > 0
    
    conditions = {
        "positive_values": Condition(Predicate().is_(is_positive))
    }
    
    schema = DeclarativeSchema(STANDARD_RESOLVER)
    for col in ["sepal_length", "sepal_width", "petal_length", "petal_width"]:
        schema.add_resolver_spec(col, metrics=[ConditionCountMetricSpec(conditions)])
    
    # Profile and validate
    profile_view = why.log(iris_df, schema=schema).profile().view()
    builder = ConstraintsBuilder(profile_view)
    
    # Add constraints for each feature
    for col in ["sepal_length", "sepal_width", "petal_length", "petal_width"]:
        builder.add_constraint(condition_meets(col, "positive_values"))
    
    constraints = builder.build()
    
    return {
        "status": "success",
        "data": map_constraints_to_whylabs(constraints.generate_constraints_report(), len(iris_df))
    }

# ==============================================
# 4. RUN THE APP (if executed directly)
# ==============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)