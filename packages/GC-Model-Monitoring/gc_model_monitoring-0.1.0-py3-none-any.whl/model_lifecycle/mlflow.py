from fastapi import FastAPI
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import gencrafter as why
import numpy as np
import os
from datetime import datetime
from typing import Dict, Any
from gencrafter.core import DatasetProfileView
import math

app = FastAPI()

def get_data() -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
    return pd.read_csv(url)

def train_model(dataframe: pd.DataFrame):
    dataframe = dataframe.copy()
    dataframe["species"] = dataframe["species"].astype("category").cat.codes
    model = DecisionTreeClassifier(max_depth=2)
    model.fit(dataframe.drop("species", axis=1), dataframe["species"])
    return "Model trained successfully!"

def clean_json_value(value):
    """Convert non-JSON-serializable values to strings"""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    elif isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        elif math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    elif isinstance(value, (list, tuple)):
        return [clean_json_value(x) for x in value]
    elif isinstance(value, dict):
        return {k: clean_json_value(v) for k, v in value.items()}
    return str(value)

def map_to_whylabs_format(
    profile_view: DatasetProfileView,
    dataset_size: int,
    model_metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Integrated mapper function with JSON sanitization"""
    # Base structure
    monitoring_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "model_status": "HEALTHY",
            "data_quality_score": 1.0
        },
        "features": {},
        "model_metadata": model_metadata or {
            "model_type": "DecisionTreeClassifier",
            "parameters": {"max_depth": 2}
        },
        "data_quality_issues": []
    }
    
    quality_metrics = []
    
    # Process each column in the profile
    for col_name in profile_view.get_columns():
        col_profile = profile_view.get_column(col_name)
        metrics_summary = {}
        
        # Get available metrics
        for metric_name, metric in col_profile._metrics.items():
            try:
                metrics_summary[metric_name] = clean_json_value(metric.to_summary_dict())
            except AttributeError:
                continue
        
        # Build feature entry
        feature_entry = {
            "counts": metrics_summary.get("counts", {}),
            "distribution": metrics_summary.get("distribution", {}),
            "types": metrics_summary.get("types", {})
        }
        
        # Calculate quality metrics
        n = feature_entry["counts"].get("n", 0)
        null_count = feature_entry["counts"].get("null", 0)
        missing_pct = null_count / dataset_size if dataset_size > 0 else 0
        feature_quality = 1.0 - missing_pct
        
        feature_entry["data_quality_score"] = feature_quality
        quality_metrics.append(feature_quality)
        
        monitoring_data["features"][col_name] = feature_entry
        
        # Flag quality issues
        if missing_pct > 0.05:
            monitoring_data["data_quality_issues"].append({
                "feature": col_name,
                "issue_type": "MISSING_VALUES",
                "severity": "HIGH" if missing_pct > 0.2 else "MEDIUM",
                "percentage_affected": missing_pct * 100
            })
    
    # Update overall scores
    if quality_metrics:
        monitoring_data["profile_summary"]["data_quality_score"] = sum(quality_metrics) / len(quality_metrics)
    
    if monitoring_data["data_quality_issues"]:
        monitoring_data["profile_summary"]["model_status"] = "WARNING"
    
    return monitoring_data

@app.get("/profile")
def profile_data():
    df = get_data()
    train_status = train_model(df)
    
    # Generate profile
    profile_result = why.log(df)
  
    # Create WhyLabs-style output
    whylabs_data = map_to_whylabs_format(
        profile_view=profile_result.view(),
        dataset_size=len(df)
    )
    
    # Convert to pandas and clean data
    profile_df = profile_result.view().to_pandas()
    cleaned_data = profile_df.replace([np.nan, np.inf, -np.inf], None)
    
    return {
        "monitoring_data": whylabs_data,
        "training_status": train_status,
        "profile_stats": cleaned_data.to_dict(orient="records")
    }