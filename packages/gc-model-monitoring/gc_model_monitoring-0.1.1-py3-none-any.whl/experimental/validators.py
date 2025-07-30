from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import gencrafter as why
from gencrafter.core.schema import DatasetSchema
from gencrafter.core.validators import ConditionValidator
from gencrafter.core.relations import Not, Predicate
from typing import Any, List, Dict
from datetime import datetime
import numpy as np

app = FastAPI()


# Define validation conditions
X = Predicate()
credit_card_conditions = {"noCreditCard": Not(X.matches(".*4[0-9]{12}(?:[0-9]{3})?"))}
email_conditions = {"hasEmail": X.fullmatch(r"[\w.]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}")}

# Define failure action
def log_failed_validation(validator_name, condition_name: str, value: Any):
    return {"validator": validator_name, "condition": condition_name, "failed_value": value}

# Create validators
credit_card_validator = ConditionValidator(
    name="no_credit_cards",
    conditions=credit_card_conditions,
    actions=[log_failed_validation],
)
email_validator = ConditionValidator(
    name="has_emails",
    conditions=email_conditions,
    actions=[log_failed_validation],
)

# Fetch dataset from online source
DATA_URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"

def get_real_data():
    df = pd.read_csv(DATA_URL)
    emails = ["user1@example.com", "invalid-email", "test@domain.com"]
    transcriptions = ["Transaction ID: 4012888888881881", "Normal text", "Another test"]
    df = pd.DataFrame({"emails": emails, "transcriptions": transcriptions})
    return df

def map_validators_to_whylabs(
    profile: Any,
    validators: Dict[str, List[ConditionValidator]],
    dataset_size: int
) -> Dict[str, Any]:
    """
    Final version with numpy type handling and complete safety checks
    """
    def convert_numpy_types(obj):
        """Recursively convert numpy types to native Python types"""
        if isinstance(obj, (np.integer, np.floating)):
            return int(obj) if isinstance(obj, np.integer) else float(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_numpy_types(x) for x in obj]
        return obj

    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": int(dataset_size),
            "validators_evaluated": sum(len(v) for v in validators.values()),
            "alert_status": "OK",
            "metrics_available": ["validations"]
        },
        "features": {},
        "validation_report": {
            "failed_validations": [],
            "summary": {
                "total": sum(len(v) for v in validators.values()),
                "passed": 0,
                "failed": 0
            }
        },
        "advanced_metrics": {
            "data_quality": {
                "missing_values": 0,
                "type_mismatches": 0
            }
        }
    }

    total_failures = 0
    total_missing = 0
    total_type_mismatches = 0

    # Safely get profile view and columns
    try:
        profile_view = profile.view() if hasattr(profile, 'view') else profile
        columns = profile_view._columns if hasattr(profile_view, '_columns') else {}
    except Exception:
        columns = {}

    # Process each column safely
    for column_name, col_metrics in columns.items():
        try:
            feature_data = {
                "validators": {},
                "basic_metrics": {
                    "count": int(dataset_size),
                    "missing": 0,
                    "inferred_type": "unknown"
                },
                "advanced_metrics": {}
            }
            
            # Get type counts
            if hasattr(col_metrics, 'get_metric'):
                try:
                    type_metric = col_metrics.get_metric("types")
                    if type_metric:
                        type_counts = {
                            "integral": int(getattr(getattr(type_metric, 'integral', None), 'value', 0)),
                            "fractional": int(getattr(getattr(type_metric, 'fractional', None), 'value', 0)),
                            "boolean": int(getattr(getattr(type_metric, 'boolean', None), 'value', 0)),
                            "string": int(getattr(getattr(type_metric, 'string', None), 'value', 0)),
                            "null": int(getattr(getattr(type_metric, 'null', None), 'value', 0))
                        }
                        feature_data["basic_metrics"].update({
                            "missing": type_counts["null"],
                            "inferred_type": max(type_counts, key=type_counts.get)
                        })
                        feature_data["advanced_metrics"]["type_counts"] = type_counts
                        total_missing += type_counts["null"]
                        if type_counts["null"] > 0:
                            total_type_mismatches += 1
                except Exception:
                    pass

            # Get distribution metrics
            if hasattr(col_metrics, 'get_metric'):
                try:
                    dist = col_metrics.get_metric("distribution")
                    if dist:
                        dist_data = {}
                        if hasattr(dist, 'mean') and hasattr(dist.mean, 'value'):
                            dist_data["mean"] = float(dist.mean.value)
                        if hasattr(dist, 'stddev') and hasattr(dist.stddev, 'value'):
                            dist_data["stddev"] = float(dist.stddev.value)
                        if hasattr(dist, 'min') and hasattr(dist.min, 'value'):
                            dist_data["min"] = float(dist.min.value)
                        if hasattr(dist, 'max') and hasattr(dist.max, 'value'):
                            dist_data["max"] = float(dist.max.value)
                        
                        if hasattr(dist, 'quantiles') and hasattr(dist.quantiles, 'values'):
                            quantiles = {}
                            values = dist.quantiles.values
                            if len(values) > 0:
                                quantiles["p01"] = float(values[0].value)
                            if len(values) > 1:
                                quantiles["p25"] = float(values[1].value)
                            if len(values) > 2:
                                quantiles["p50"] = float(values[2].value)
                            if len(values) > 3:
                                quantiles["p75"] = float(values[3].value)
                            if len(values) > 4:
                                quantiles["p99"] = float(values[4].value)
                            dist_data["quantiles"] = quantiles
                        
                        feature_data["advanced_metrics"]["distribution"] = dist_data
                except Exception:
                    pass

            # Get cardinality
            if hasattr(col_metrics, 'get_metric'):
                try:
                    card = col_metrics.get_metric("cardinality")
                    if card and hasattr(card, 'hll') and hasattr(card.hll, 'value'):
                        hll = card.hll.value
                        unique = int(hll.get_estimate()) if hasattr(hll, 'get_estimate') else 0
                        feature_data["advanced_metrics"]["cardinality"] = {
                            "unique_count": unique,
                            "est_unique": unique
                        }
                except Exception:
                    pass

            whylabs_data["features"][column_name] = feature_data

        except Exception:
            continue

    # Process validators
    for column_name, column_validators in validators.items():
        for validator in column_validators:
            try:
                failures = validator.get_samples() if hasattr(validator, 'get_samples') else []
                failure_count = len(failures)
                
                # Get condition definitions
                condition_defs = {}
                if hasattr(validator, 'conditions'):
                    for name, condition in validator.conditions.items():
                        try:
                            if hasattr(condition, 'predicate'):
                                condition_defs[name] = str(condition.predicate)
                            elif hasattr(condition, '_predicate'):
                                condition_defs[name] = str(condition._predicate)
                            else:
                                condition_defs[name] = "Unknown condition"
                        except Exception:
                            condition_defs[name] = "Condition parsing failed"
                
                # Initialize feature if not exists
                if column_name not in whylabs_data["features"]:
                    whylabs_data["features"][column_name] = {
                        "validators": {},
                        "basic_metrics": {
                            "count": int(dataset_size),
                            "missing": 0,
                            "inferred_type": "unknown"
                        },
                        "advanced_metrics": {}
                    }
                
                whylabs_data["features"][column_name]["validators"][validator.name] = {
                    "conditions": list(validator.conditions.keys()) if hasattr(validator, 'conditions') else [],
                    "failure_count": int(failure_count),
                    "status": "FAIL" if failure_count > 0 else "PASS",
                    "failed_samples": [str(x) for x in failures[:5]],  # Ensure strings
                    "condition_definitions": condition_defs
                }

                if failure_count > 0:
                    total_failures += 1
                    whylabs_data["validation_report"]["failed_validations"].append({
                        "feature": column_name,
                        "validator": validator.name,
                        "failure_count": int(failure_count),
                        "conditions": list(validator.conditions.keys()) if hasattr(validator, 'conditions') else [],
                        "samples": [str(x) for x in failures[:3]],  # Ensure strings
                        "condition_definitions": condition_defs
                    })

            except Exception:
                continue

    # Update summary metrics
    whylabs_data["validation_report"]["summary"].update({
        "passed": int(whylabs_data["validation_report"]["summary"]["total"] - total_failures),
        "failed": int(total_failures)
    })
    
    total_columns = len(columns) if columns else 1
    whylabs_data["advanced_metrics"]["data_quality"].update({
        "missing_values": int(total_missing),
        "missing_percentage": float((total_missing / (dataset_size * total_columns)) * 100 if dataset_size * total_columns > 0 else 0),
        "type_mismatches": int(total_type_mismatches)
    })

    if total_failures > 0 or total_missing > 0:
        whylabs_data["profile_summary"]["alert_status"] = "WARNING"
    
    # Add inferred schema
    whylabs_data["profile_summary"]["inferred_schema"] = {
        col: whylabs_data["features"][col]["basic_metrics"]["inferred_type"]
        for col in columns if col in whylabs_data["features"]
    }

    # Update available metrics
    available_metrics = ["validations"]
    for col_data in whylabs_data["features"].values():
        if "distribution" in col_data["advanced_metrics"]:
            if "distribution" not in available_metrics:
                available_metrics.append("distribution")
        if "type_counts" in col_data["advanced_metrics"]:
            if "type_counts" not in available_metrics:
                available_metrics.append("type_counts")
        if "cardinality" in col_data["advanced_metrics"]:
            if "cardinality" not in available_metrics:
                available_metrics.append("cardinality")
    
    whylabs_data["profile_summary"]["metrics_available"] = available_metrics

    # Convert all numpy types to native Python types
    return convert_numpy_types(whylabs_data)
@app.post("/validate")
def validate_data():
    df = get_real_data()

    # Bind validators to columns
    validators = {
        "emails": [email_validator], 
        "transcriptions": [credit_card_validator]
    }
    schema = DatasetSchema(validators=validators)
    profile = why.log(df, schema=schema).profile()

    # Generate WhyLabs-style output
    whylabs_data = map_validators_to_whylabs(
        profile=profile,
        validators=validators,
        dataset_size=len(df)
    )

    return {
        "whylabs_formatted_data": whylabs_data,
        "original_failures": {
            "email": email_validator.get_samples(),
            "credit_card": credit_card_validator.get_samples()
        }
    }