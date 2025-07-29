from fastapi import FastAPI
import pandas as pd
import gencrafter as why
import numpy as np
from datetime import datetime
from typing import Dict, Any
from gencrafter.core import DatasetProfileView
from gencrafter.core.schema import DeclarativeSchema
from gencrafter.core.resolvers import STANDARD_RESOLVER
import os

app = FastAPI()


def clean_float_values(data: Any) -> Any:
    """Recursively clean float values to be JSON serializable"""
    if isinstance(data, float):
        if np.isinf(data) or np.isnan(data):
            return None
        return data
    elif isinstance(data, dict):
        return {k: clean_float_values(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [clean_float_values(x) for x in data]
    return data

def map_to_whylabs_format(profile_view: DatasetProfileView, dataset_size: int) -> Dict[str, Any]:
    """Map gencrafter profile to WhyLabs-compatible format"""
    profile_columns = profile_view.get_columns()
    
    mapped_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "columns_tracked": len(profile_columns),
            "missing_cells": sum(
                col_metrics._metrics["counts"].null.value 
                for col_metrics in profile_columns.values() 
                if "counts" in col_metrics._metrics
            ),
        },
        "features": {}
    }
    
    for feature_name, column_metrics in profile_columns.items():
        counts = column_metrics._metrics.get("counts")
        distribution = column_metrics._metrics.get("distribution")
        frequent_items = column_metrics._metrics.get("frequent_items")
        
        feature_data = {
            "counts": {
                "count": counts.n.value if counts else 0,
                "missing": counts.null.value if counts else 0,
            }
        }
        
        if distribution:
            feature_data["distribution"] = clean_float_values({
                "mean": distribution.mean.value,
                "stddev": distribution.stddev,
                "min": distribution.min,
                "max": distribution.max,
                "quantiles": {
                    "0.25": distribution.q_25,
                    "0.50": distribution.median,
                    "0.75": distribution.q_75
                }
            })
        
        if frequent_items:
            # Handle both old and new gencrafter frequent items format
            freq_items = []
            if hasattr(frequent_items, 'to_summary_dict'):
                summary = frequent_items.to_summary_dict()
                if isinstance(summary.get('frequent_strings'), dict):
                    freq_items = [{"value": k, "count": v} for k, v in summary['frequent_strings'].items()]
                elif isinstance(summary.get('items'), list):
                    freq_items = [{"value": x['value'], "count": x['estimate']} for x in summary['items']]
            
            feature_data["string_metrics"] = {
                "frequent_items": freq_items
            }
        
        mapped_data["features"][feature_name] = feature_data
    
    return mapped_data

def fetch_iris_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    col_names = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
    return pd.read_csv(url, names=col_names)

@app.get("/profile")
def profile_data():
    schema = DeclarativeSchema(STANDARD_RESOLVER)
    df = fetch_iris_data()
    result = why.log(df, schema=schema)
    profile_view = result.view()
    
    # Get raw profile data
    raw_profile_df = profile_view.to_pandas()
    raw_profile = clean_float_values(raw_profile_df.to_dict())
    
    # Convert to WhyLabs format
    whylabs_data = map_to_whylabs_format(profile_view, len(df))
    
    
    return {
        "input_data": df.to_dict(orient='records'),
        "raw_profile": raw_profile,
        "whylabs_formatted": whylabs_data,
        "message": "Successfully processed iris dataset"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)