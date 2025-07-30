from fastapi import FastAPI
import pandas as pd
import numpy as np
import gencrafter as why
from gencrafter.core.resolvers import STANDARD_RESOLVER
from gencrafter.core.specialized_resolvers import ConditionCountMetricSpec
from gencrafter.core.metrics.condition_count_metric import Condition
from gencrafter.core.relations import Predicate, Not
from gencrafter.core.schema import DeclarativeSchema
import zipfile
import requests
from io import BytesIO


app = FastAPI()


def log_data(df: pd.DataFrame, schema: DeclarativeSchema):
    try:
        # ✅ Create profile
        prof = why.log(df, schema=schema).profile()

        if prof is None:
            raise ValueError("Profile generation failed. Check schema and data.")

        # ✅ Debugging - Print profile details
        print("Profile Created:", prof)
        print("Profile Summary:", prof.view().to_pandas())

        print("✅ Successfully written to WhyLabs")

        return prof.view().to_pandas().to_dict()
    
    except Exception as e:
        print(f"🚨 Error in logging data: {e}")
        return {"error": str(e)}

def sanitize_dict(d):
    """ Recursively replace NaN, inf, and -inf in a dictionary with None """
    if isinstance(d, dict):
        return {k: sanitize_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [sanitize_dict(v) for v in d]
    elif isinstance(d, float):
        if np.isnan(d) or np.isinf(d):
            return None
    return d


@app.get("/profile/emails")
def profile_emails():
    url = "https://archive.ics.uci.edu/static/public/94/spambase.zip"
    response = requests.get(url)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        with z.open("spambase.data") as f:
            df = pd.read_csv(f, header=None)
    
    data = {"emails": df.iloc[:, 0].dropna().sample(10, random_state=42).tolist()}
    df_sample = pd.DataFrame(data)

    emails_conditions = {
        "containsEmail": Condition(Predicate().matches(r"[\w.]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}")),
    }
    
    schema = DeclarativeSchema(STANDARD_RESOLVER)
    schema.add_resolver_spec(column_name="emails", metrics=[ConditionCountMetricSpec(emails_conditions)])

    print("Schema defined for emails profiling:", schema)

    profile = log_data(df_sample, schema)
    return sanitize_dict(profile)

@app.get("/profile/numbers")
def profile_numbers():
    data = {
        "ints_column": [1, 12, 42, 4],
        "floats_column": [1.2, 12.3, 42.2, 4.8]
    }
    df = pd.DataFrame(data)

    conditions = {
        "between10and50": Condition(Predicate().greater_than(10).and_(Predicate().less_than(50))),
        "outside10and50": Condition(Predicate().less_than(10).or_(Predicate().greater_than(50))),
        "not_42": Condition(Not(Predicate().equals(42)))
    }
    schema = DeclarativeSchema(STANDARD_RESOLVER)
    schema.add_resolver_spec(column_name="ints_column", metrics=[ConditionCountMetricSpec(conditions)])
    schema.add_resolver_spec(column_name="floats_column", metrics=[ConditionCountMetricSpec(conditions)])

    print("Schema defined for numbers profiling:", schema)

    profile = log_data(df, schema)
    return sanitize_dict(profile)