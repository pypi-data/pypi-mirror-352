import joblib
import pandas as pd
import requests
from io import StringIO
from sklearn import neighbors
from sklearn.model_selection import train_test_split
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import gencrafter as why
import os

# URL of the Wine Quality dataset
CSV_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"

# Fetch dataset from the URL
response = requests.get(CSV_URL)
if response.status_code == 200:
    data_wine = pd.read_csv(StringIO(response.text), sep=";")  # CSV uses ';' as delimiter
    print("Wine dataset loaded successfully from URL!")
else:
    raise Exception(f"Failed to fetch CSV. HTTP Status: {response.status_code}")

# Extract features and target
X = data_wine.iloc[:, :-1]  # All columns except the last one (features)
y = data_wine.iloc[:, -1]   # Last column (target: wine quality)

# Split into training and testing datasets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize model
knn = neighbors.KNeighborsClassifier(n_neighbors=5)

# Train the model
trained_model = knn.fit(X_train, y_train)

# Save trained model
joblib.dump(trained_model, "knn_model.pkl")
print("Model trained and saved using Wine Quality dataset from URL!")

# Load model
model = joblib.load("knn_model.pkl")

# Get feature names and class labels dynamically
CLASS_NAMES = sorted(y.unique().tolist())  # Unique wine quality values

# Set WhyLabs environment variables
os.environ["WHYLABS_DEFAULT_ORG_ID"] = "org-vbRHaH"
os.environ["WHYLABS_DEFAULT_DATASET_ID"] = "model-2"
os.environ["WHYLABS_API_KEY"] = "wKt2wLAtIJ.0NeFb3K8U3ziSHa30wFzJNdb6LInhJCqUtfaOicOE8iqsPdhBV2lu:org-vbRHaH"

app = FastAPI()

# ✅ Fix: Explicitly define Pydantic Model
class PredictRequest(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

# Create prediction function
def make_prediction(model, features):
    results = model.predict(features)
    probs = model.predict_proba(features)
    result = results[0]

    output_cls = CLASS_NAMES[result]
    output_proba = max(probs[0])

    return (output_cls, output_proba)

# API Endpoint for prediction
@app.post("/predict")
def predict(request: PredictRequest) -> JSONResponse:
    data = jsonable_encoder(request)
    features = list(data.values())

    # Make prediction
    predictions = make_prediction(model, [features])
    data["model_class_output"] = predictions[0]
    data["model_prob_output"] = predictions[1]

    # Log input data with gencrafter & write to WhyLabs
    profile_results = why.log(data)
    profile_results.writer("whylabs").write()

    return JSONResponse(data)
