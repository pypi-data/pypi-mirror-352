from fastapi import FastAPI
import os
import pandas as pd
import gencrafter as why
from datetime import datetime, timezone
from gencrafter.core.view.dataset_profile_view import DatasetProfileView
from typing import Dict, Any

app = FastAPI()

# Load the dataset - Using Iris dataset
csv_url = "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv"
df = pd.read_csv(csv_url)

def safe_get_metric(metric_obj, attr_name, default=None):
    """Safely get metric value whether it's a metric object or raw value"""
    if hasattr(metric_obj, attr_name):
        attr = getattr(metric_obj, attr_name)
        return attr.value if hasattr(attr, 'value') else attr
    return default

def map_profile_to_whylabs(
    profile_view: DatasetProfileView,
    dataset_size: int
) -> Dict[str, Any]:
    """
    Final corrected mapper for current gencrafter version
    Handles both metric objects and raw values
    """
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "columns_monitored": len(profile_view.get_columns()),
            "dataset_timestamp": profile_view.dataset_timestamp.isoformat() if profile_view.dataset_timestamp else "",
        },
        "features": {},
        "data_quality_metrics": {
            "missing_values": 0,
            "type_mismatches": 0
        }
    }

    for col_name in profile_view.get_columns():
        col_profile = profile_view.get_column(col_name)
        metrics = col_profile._metrics
        
        # Initialize with defaults
        feature_data = {
            "counts": {
                "count": 0,
                "missing": 0,
                "null": 0
            },
            "types": {
                "type": "unknown",
                "inferred_type": "unknown"
            },
            "distribution": {
                "mean": None,
                "stddev": None,
                "min": None,
                "max": None,
                "quantiles": {
                    "0.25": None,
                    "0.5": None,
                    "0.75": None
                }
            }
        }

        # Handle counts
        if "counts" in metrics:
            counts = metrics["counts"]
            feature_data["counts"]["count"] = safe_get_metric(counts, "n", 0)
        
        # Handle types and missing values
        if "types" in metrics:
            types = metrics["types"]
            feature_data["types"]["type"] = str(safe_get_metric(types, "type", "unknown"))
            feature_data["types"]["inferred_type"] = str(safe_get_metric(types, "inferred_type", "unknown"))
            
            # Different versions handle null counts differently
            if hasattr(types, "null"):
                feature_data["counts"]["null"] = safe_get_metric(types, "null", 0)
                feature_data["counts"]["missing"] = feature_data["counts"]["null"]
            elif hasattr(types, "missing"):
                feature_data["counts"]["missing"] = safe_get_metric(types, "missing", 0)
        
        # Handle distribution
        if "distribution" in metrics:
            dist = metrics["distribution"]
            feature_data["distribution"].update({
                "mean": safe_get_metric(dist, "mean"),
                "stddev": safe_get_metric(dist, "stddev"),
                "min": safe_get_metric(dist, "min"),
                "max": safe_get_metric(dist, "max"),
                "quantiles": {
                    "0.25": safe_get_metric(dist, "q_25"),
                    "0.5": safe_get_metric(dist, "median"),
                    "0.75": safe_get_metric(dist, "q_75")
                }
            })
        
        whylabs_data["features"][col_name] = feature_data
        
        # Update data quality metrics
        whylabs_data["data_quality_metrics"]["missing_values"] += feature_data["counts"]["missing"]
        if "types" in metrics:
            types = metrics["types"]
            if hasattr(types, "unexpected_count"):
                unexpected = safe_get_metric(types, "unexpected_count", 0)
                whylabs_data["data_quality_metrics"]["type_mismatches"] += unexpected

    return whylabs_data

@app.get("/log_profile")
def log_profile():
    try:
        # Log the dataset
        profile = why.log(df, dataset_timestamp=datetime.now(tz=timezone.utc)).profile()
        profile_view = profile.view()
        
        # Generate WhyLabs-style output
        whylabs_data = map_profile_to_whylabs(
            profile_view=profile_view,
            dataset_size=len(df)
        )
        
        return {
            "message": "Profile logged successfully!",
            "whylabs_formatted_data": whylabs_data,
            "dataset_summary": df.describe().to_dict()
        }
    except Exception as e:
        return {"error": str(e)}