from fastapi import FastAPI
import pandas as pd
import gencrafter as why
from gencrafter.api.writer.whylabs import WhyLabsWriter
from typing import Any
from gencrafter.experimental.core.validators import condition_validator
from gencrafter.experimental.core.udf_schema import udf_schema, register_dataset_udf
import requests
import io
import zipfile



app = FastAPI()

# ✅ Load dataset
url = "https://archive.ics.uci.edu/static/public/94/spambase.zip"
response = requests.get(url)
with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
    file_name = [name for name in zip_ref.namelist() if name.endswith(".data")][0]
    with zip_ref.open(file_name) as file:
        df = pd.read_csv(file, header=None)

# ✅ Assign column names
column_names = [
    "word_freq_make", "word_freq_address", "word_freq_all", "word_freq_3d", "word_freq_our", "word_freq_over",
    "word_freq_remove", "word_freq_internet", "word_freq_order", "word_freq_mail", "word_freq_receive",
    "word_freq_will", "word_freq_people", "word_freq_report", "word_freq_addresses", "word_freq_free",
    "word_freq_business", "word_freq_email", "word_freq_you", "word_freq_credit", "word_freq_your", "word_freq_font",
    "word_freq_000", "word_freq_money", "word_freq_hp", "word_freq_hpl", "word_freq_george", "word_freq_650",
    "word_freq_lab", "word_freq_labs", "word_freq_telnet", "word_freq_857", "word_freq_data", "word_freq_415",
    "word_freq_85", "word_freq_technology", "word_freq_1999", "word_freq_parts", "word_freq_pm", "word_freq_direct",
    "word_freq_cs", "word_freq_meeting", "word_freq_original", "word_freq_project", "word_freq_re", "word_freq_edu",
    "word_freq_table", "word_freq_conference", "char_freq_;", "char_freq_(", "char_freq_[", "char_freq_!",
    "char_freq_$", "char_freq_#", "capital_run_length_average", "capital_run_length_longest", "capital_run_length_total", "spam"
]
df.columns = column_names

# ✅ Custom condition validators
def do_something_important(validator_name, condition_name: str, value: Any, column_id=None):
    return {"validator": validator_name, "condition": condition_name, "failed_value": value}

@condition_validator(["word_freq_make"], condition_name="less_than_four", actions=[do_something_important])
def lt_4(x):
    return x < 4

@register_dataset_udf(["word_freq_make"])
def add5(x):
    return [xx + 5 for xx in x["word_freq_make"]]

@condition_validator(["add5"], condition_name="greater_than_ten", actions=[do_something_important])
def gt_10(x):
    return x > 10

# ✅ FastAPI Endpoints
@app.get("/validate_col1")
def validate_col1():
    schema = udf_schema()
    why.log(df, schema=schema)
    failed_samples = schema.validators.get("word_freq_make", [])
    failed_samples = failed_samples[0].get_samples() if failed_samples else []
    return {"failed_samples": failed_samples}

@app.get("/validate_add5")
def validate_add5():
    schema = udf_schema()
    transformed_data = df.copy()
    transformed_data["add5"] = add5(df)
    why.log(transformed_data, schema=schema)
    failed_samples = schema.validators.get("add5", [])
    failed_samples = failed_samples[0].get_samples() if failed_samples else []
    return {"failed_samples": failed_samples}

@app.get("/log_to_whylabs")
def log_to_whylabs():
    try:
        schema = udf_schema()
        profile = why.log(df, schema=schema)  # ✅ Include schema

        # ✅ Print detailed summary before sending to WhyLabs
        print("Profile Summary:\n", profile.view().to_pandas())  # ✅ Converts profile to readable format

    except Exception as e:
        return {"status": "error", "message": str(e)}
