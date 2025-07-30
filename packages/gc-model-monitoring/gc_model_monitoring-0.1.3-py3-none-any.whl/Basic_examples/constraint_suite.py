from fastapi import FastAPI
import gencrafter as why
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any
from gencrafter.core import DatasetProfile
from gencrafter.core.constraints import Constraints, ConstraintsBuilder
from gencrafter.core.constraints.factories import (
    greater_than_number,
    mean_between_range,
    smaller_than_number,
    stddev_between_range,
    quantile_between_range,
    is_in_range,
    is_non_negative
)

app = FastAPI()



# URL of the online dataset
CSV_URL = "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv"

# Load dataset with error handling
try:
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.replace('"', '')  # Clean column names
    print("Loaded dataset with columns:", df.columns.tolist())  # Debugging
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = None  # Avoid using an invalid dataset
    
    

def map_constraint_suite_to_whylabs(
    profile_view: DatasetProfile,
    constraints: Constraints,
    dataset_size: int,
    column_names: list
) -> Dict[str, Any]:
    """
    Fixed mapper that correctly handles ColumnProfileView objects
    """
    constraints_report = constraints.generate_constraints_report()
    
    # Initialize the output structure
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "constraints_evaluated": len(constraints_report),
            "constraints_passed": sum(1 for r in constraints_report if r.passed),
            "alert_status": "OK"
        },
        "features": {},
        "constraints_report": {
            "constraints": [],
            "summary": {
                "total": len(constraints_report),
                "passed": sum(1 for r in constraints_report if r.passed),
                "failed": sum(1 for r in constraints_report if not r.passed)
            }
        },
        "data_quality_issues": []
    }

    # Initialize feature structures
    for col in column_names:
        col_profile = profile_view.get_column(col)
        summary = col_profile.to_summary_dict() if col_profile else {}
        
        whylabs_data["features"][col] = {
            "constraints": {},
            "basic_metrics": {
                "counts": {
                    "count": dataset_size,
                    "missing": summary.get("counts/n", 0),
                    "null": summary.get("counts/null", 0)
                },
                "distribution": {
                    "mean": summary.get("distribution/mean"),
                    "stddev": summary.get("distribution/stddev"),
                    "min": summary.get("distribution/min"),
                    "max": summary.get("distribution/max"),
                    "median": summary.get("distribution/median") or summary.get("distribution/quantiles/0.5"),
                    "q_25": summary.get("distribution/quantiles/0.25"),
                    "q_75": summary.get("distribution/quantiles/0.75")
                } if any(k.startswith("distribution/") for k in summary) else None
            },
            "condition_metrics": {}
        }

    # Process each constraint
    for i, constraint in enumerate(constraints_report, 1):
        constraint_name = str(constraint)
        
        # Extract feature name from constraint
        feature_name = None
        if hasattr(constraint, 'column_name'):
            feature_name = constraint.column_name
        else:
            # Fallback: find which column this constraint refers to
            for col in column_names:
                if col in constraint_name:
                    feature_name = col
                    break
        
        if not feature_name or feature_name not in whylabs_data["features"]:
            continue
            
        # Create constraint ID
        constraint_id = f"constraint_{i}"
        
        # Get metric value if available
        metric_value = None
        if hasattr(constraint, 'metric'):
            metric_value = constraint.metric
        elif hasattr(constraint, 'value'):
            metric_value = constraint.value
            
        # Clean up condition string
        condition = constraint_name
        if feature_name in condition:
            condition = condition.split(feature_name)[-1].strip()
        
        # Add to feature's constraints
        whylabs_data["features"][feature_name]["constraints"][constraint_id] = {
            "name": constraint_name,
            "status": "PASS" if constraint.passed else "FAIL",
            "condition": condition,
            "actual_value": metric_value
        }
        
        # Add to constraints report
        whylabs_data["constraints_report"]["constraints"].append({
            "name": constraint_name,
            "status": "PASS" if constraint.passed else "FAIL",
            "feature": feature_name,
            "condition": condition,
            "actual_value": metric_value
        })
        
        # Add to data quality issues if failed
        if not constraint.passed:
            whylabs_data["data_quality_issues"].append({
                "feature": feature_name,
                "issue_type": "CONSTRAINT_VIOLATION",
                "severity": "HIGH",
                "constraint": constraint_name,
                "condition": condition,
                "actual_value": metric_value
            })

    # Update alert status if any constraints failed
    if whylabs_data["constraints_report"]["summary"]["failed"] > 0:
        whylabs_data["profile_summary"]["alert_status"] = "WARNING"

    return whylabs_data

@app.get("/schema-configure")
def run_schema_configure():
    if df is None:
        return {"error": "Dataset not loaded properly. Check CSV URL or format."}

    # Generate gencrafter profile
    results = why.log(df)
    profile_view = results.view()


    # Define constraints
    builder = ConstraintsBuilder(dataset_profile_view=profile_view)
    column_names = df.columns.tolist()

    # Check if expected columns exist
    if "Height(Inches)" not in column_names or "Weight(Pounds)" not in column_names:
        return {"error": "Expected columns not found. Available columns: " + str(column_names)}

    # Add constraints
    builder.add_constraint(greater_than_number(column_name="Height(Inches)", number=40))
    builder.add_constraint(mean_between_range(column_name="Weight(Pounds)", lower=100, upper=200))
    builder.add_constraint(smaller_than_number(column_name="Weight(Pounds)", number=300))
    builder.add_constraint(stddev_between_range(column_name="Weight(Pounds)", lower=5, upper=50))
    builder.add_constraint(quantile_between_range(column_name="Weight(Pounds)", quantile=0.5, lower=120, upper=180))
    builder.add_constraint(is_in_range(column_name="Height(Inches)", lower=50, upper=80))
    builder.add_constraint(is_non_negative(column_name="Height(Inches)"))

    constraints = builder.build()

    # Generate WhyLabs-style output
    whylabs_data = map_constraint_suite_to_whylabs(
        profile_view=profile_view,
        constraints=constraints,
        dataset_size=len(df),
        column_names=column_names
    )

    # Also get the original validation results
    validation_details = [
        {
            "constraint": result[0],
            "passed": result[1],
            "failed": result[2]
        }
        for result in constraints.report()
    ]

    return {
        "whylabs_formatted_data": whylabs_data,
        "original_validation_results": validation_details
    }