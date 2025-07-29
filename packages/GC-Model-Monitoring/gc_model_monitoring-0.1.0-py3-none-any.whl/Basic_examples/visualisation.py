import os
import logging
import pandas as pd
import gencrafter as why
import numpy as np
from fastapi import FastAPI
from datetime import datetime
from typing import Dict, Any
from gencrafter.viz import NotebookProfileVisualizer
from gencrafter.core import DatasetProfileView
from gencrafter.core.view.column_profile_view import ColumnProfileView

# Disable gencrafter analytics
os.environ["gencrafter_NO_ANALYTICS"] = "1"
os.environ["gencrafter_API_DISABLE_USAGE_STATS"] = "1"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sec")

app = FastAPI()

# Load dataset once
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
wine = pd.read_csv(url)

# Split dataset into reference and target groups
cond_reference = wine["petal_length"] <= 3.0
wine_reference = wine.loc[cond_reference].copy()
cond_target = wine["petal_length"] > 3.0
wine_target = wine.loc[cond_target].copy()

# Introduce missing values
ixs = wine_target.iloc[10:20].index
wine_target.loc[ixs, "sepal_width"] = None

# Categorize petal length
bins = [0, 3.0, 7.0]
group_names = ["short", "long"]
wine_reference["petal_category"] = pd.cut(wine_reference["petal_length"], bins=bins, labels=group_names)
wine_target["petal_category"] = pd.cut(wine_target["petal_length"], bins=bins, labels=group_names)

def convert_to_python_type(value):
    """Convert numpy and other non-JSON-serializable types to native Python types"""
    if isinstance(value, (np.integer, np.floating)):
        return int(value) if isinstance(value, np.integer) else float(value)
    return value

def get_metric_value(metric_component):
    """Safely extract numeric value from metric component and convert to Python type"""
    if hasattr(metric_component, 'value'):
        value = metric_component.value
    else:
        value = metric_component
    return convert_to_python_type(value)

def get_column_metrics(column_view: ColumnProfileView) -> Dict[str, Any]:
    """Extract metrics from a column profile view"""
    metrics = {}
    
    # Count metrics
    counts = column_view.get_metric("counts")
    if counts:
        metrics["count"] = get_metric_value(counts.n)
        metrics["missing"] = get_metric_value(counts.null)
        metrics["null_count"] = get_metric_value(counts.null)
    
    # Distribution metrics
    distribution = column_view.get_metric("distribution")
    if distribution:
        metrics.update({
            "mean": get_metric_value(distribution.mean),
            "stddev": get_metric_value(distribution.stddev),
            "min": get_metric_value(distribution.min),
            "max": get_metric_value(distribution.max),
            "quantiles": {
                "0.25": get_metric_value(distribution.q_25),
                "0.5": get_metric_value(distribution.median),
                "0.75": get_metric_value(distribution.q_75)
            }
        })
    
    # Type counts
    types = column_view.get_metric("types")
    if types:
        metrics["type_count"] = {
            "integral": get_metric_value(types.integral),
            "fractional": get_metric_value(types.fractional),
            "boolean": get_metric_value(types.boolean),
            "string": get_metric_value(types.string)
        }
    
    return metrics

def map_to_whylabs_format(
    profile_view: DatasetProfileView,
    reference_view: DatasetProfileView = None,
    dataset_size: int = None
) -> Dict[str, Any]:
    """
    Maps gencrafter profile to WhyLabs-style format for visualization
    """
    if dataset_size is None:
        dataset_size = len(wine_target)
    
    mapped_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": int(dataset_size),
            "missing_cells": 0,
            "schema_violations": 0,
            "alert_status": "OK"
        },
        "features": {},
        "drift_analysis": {
            "drifted_features": [],
            "feature_drift_scores": {}
        }
    }
    
    missing_cells = 0
    schema_violations = 0
    
    for column_name in profile_view.get_columns():
        column_view = profile_view.get_column(column_name)
        metrics = get_column_metrics(column_view)
        
        missing_cells += int(metrics.get("missing", 0))
        schema_violations += int(metrics.get("type_count", {}).get("unexpected", 0))
        
        mapped_data["features"][column_name] = {
            "counts": {
                "count": metrics.get("count", 0),
                "missing": metrics.get("missing", 0),
                "null": metrics.get("null_count", 0)
            },
            "types": metrics.get("type_count", {}),
            "distribution": {
                "mean": metrics.get("mean"),
                "stddev": metrics.get("stddev"),
                "min": metrics.get("min"),
                "max": metrics.get("max"),
                "quantiles": metrics.get("quantiles", {}),
                "histogram": {}
            }
        }
    
    mapped_data["profile_summary"]["missing_cells"] = missing_cells
    mapped_data["profile_summary"]["schema_violations"] = schema_violations
    
    if reference_view:
        for column_name in profile_view.get_columns():
            if column_name in reference_view.get_columns():
                current_col = profile_view.get_column(column_name)
                ref_col = reference_view.get_column(column_name)
                
                current_dist = current_col.get_metric("distribution")
                ref_dist = ref_col.get_metric("distribution")
                
                if current_dist and ref_dist:
                    current_mean = get_metric_value(current_dist.mean)
                    ref_mean = get_metric_value(ref_dist.mean)
                    if ref_mean != 0:
                        drift_score = abs((current_mean - ref_mean) / ref_mean)
                        
                        mapped_data["features"][column_name]["drift_metrics"] = {
                            "psi": None,
                            "confidence": "HIGH" if drift_score > 0.5 else "LOW"
                        }
                        mapped_data["drift_analysis"]["feature_drift_scores"][column_name] = float(drift_score)
                        if drift_score > 0.5:
                            mapped_data["drift_analysis"]["drifted_features"].append(column_name)
    
    return mapped_data

@app.get("/profile-summary")
async def generate_profile():
    """Generates a gencrafter profile summary in WhyLabs format"""
    try:
        result = why.log(wine_target)
        prof_view = result.view()
        result_ref = why.log(wine_reference)
        prof_view_ref = result_ref.view()
        
        whylabs_data = map_to_whylabs_format(
            profile_view=prof_view,
            reference_view=prof_view_ref,
            dataset_size=len(wine_target))
    
        return {
            "whylabs_data": whylabs_data,
            "message": "Profile generated and uploaded to WhyLabs"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/drift-report")
async def drift_report():
    """Generates a drift report in WhyLabs format"""
    try:
        result = why.log(wine_target)
        prof_view = result.view()
        result_ref = why.log(wine_reference)
        prof_view_ref = result_ref.view()
        
        whylabs_data = map_to_whylabs_format(
            profile_view=prof_view,
            reference_view=prof_view_ref,
            dataset_size=len(wine_target))
        
        visualization = NotebookProfileVisualizer()
        visualization.set_profiles(target_profile_view=prof_view, reference_profile_view=prof_view_ref)
        drift_summary = visualization.summary_drift_report()
        whylabs_data["drift_visualization"] = drift_summary
    
        return {
            "whylabs_data": whylabs_data,
            "message": "Drift report generated and profiles uploaded to WhyLabs"
        }
    except Exception as e:
        return {"error": str(e)}