from fastapi import FastAPI
import pandas as pd
import gencrafter as why
from gencrafter.viz.drift.column_drift_algorithms import calculate_drift_scores
import zipfile
import requests
import io
import numpy as np
from fastapi.responses import JSONResponse
import os

# In your drift detection FastAPI file
from drift_mapper import map_drift_to_whylabs, clean_json



app = FastAPI()

# ✅ Initialize WhyLabs writer securely

# ✅ Prevent re-downloading every time
DATA_FILE_PATH = "./data/Online Retail.xlsx"

def download_and_extract_data():
    if not os.path.exists(DATA_FILE_PATH):
        print("Downloading dataset...")
        url = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
        response = requests.get(url)
        os.makedirs("./data", exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_ref:
            zip_ref.extractall("./data")
    return DATA_FILE_PATH

def load_data():
    file_path = download_and_extract_data()
    return pd.read_excel(file_path)

# ✅ Generate gencrafter profiles at startup
def generate_profiles():
    df = load_data().dropna()  # Remove missing values
    target_df = df.sample(frac=0.5, random_state=42)
    reference_df = df.drop(target_df.index)

    target_view = why.log(target_df).profile().view()
    reference_view = why.log(reference_df).profile().view()

    return target_view, reference_view

# 🔄 Cache profiles instead of re-generating every request
target_view, reference_view = generate_profiles()


@app.get("/calculate_drift")
async def calculate_drift():
    try:
        # Calculate drift scores (existing code)
        scores = calculate_drift_scores(
            target_view=target_view,
            reference_view=reference_view,
            with_thresholds=True
        )
        
        # Generate WhyLabs-style output
        whylabs_data = map_drift_to_whylabs(
            target_view=target_view,
            reference_view=reference_view,
            drift_scores=scores,
            dataset_size=len(target_view.to_pandas()) if hasattr(target_view, 'to_pandas') else 0
        )
        
        # Return both raw and mapped data
        return JSONResponse(content={
            "whylabs_mapped_data": clean_json(whylabs_data),
            "raw_drift_scores": clean_json(scores)
        })
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )