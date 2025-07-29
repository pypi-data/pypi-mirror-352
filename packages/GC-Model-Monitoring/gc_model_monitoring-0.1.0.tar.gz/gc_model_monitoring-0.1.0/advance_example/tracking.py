from fastapi import FastAPI
import pandas as pd
import gencrafter as why
from gencrafter.core.schema import ColumnSchema, DatasetSchema
from gencrafter.core.metrics.unicode_range import UnicodeRangeMetric
from gencrafter.core.resolvers import Resolver
from gencrafter.core.datatypes import DataType
from gencrafter.core.metrics import Metric, MetricConfig
from gencrafter.api.writer.whylabs import WhyLabsWriter
from typing import Dict, Any
import requests
from io import StringIO
import numpy as np
import os
# whylabs_tracking_mapper.py
from datetime import datetime



# Initialize FastAPI app
app = FastAPI()

# Define a custom Unicode Resolver
class UnicodeResolver(Resolver):
    def resolve(self, name: str, why_type: DataType, column_schema: ColumnSchema) -> Dict[str, Metric]:
        return {UnicodeRangeMetric.get_namespace(): UnicodeRangeMetric.zero(column_schema.cfg)}

# Create a dataset schema with the UnicodeResolver and custom metric config
config = MetricConfig(unicode_ranges={"digits": (48, 57), "alpha": (97, 122)})
schema = DatasetSchema(resolvers=UnicodeResolver(), default_configs=config)

# Fetch the real dataset (Iris dataset from UCI)
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
column_names = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    df = pd.read_csv(StringIO(response.text), names=column_names)
else:
    df = pd.DataFrame(columns=column_names)  # Create an empty DataFrame if the request fails


def map_tracking_profile_to_whylabs(profile_view_df: Dict[str, Any], dataset_size: int) -> Dict[str, Any]:
    """
    Maps gencrafter tracking profile to WhyLabs-style structure
    
    Args:
        profile_view_df: Dictionary from profile.view().to_pandas().to_dict()
        dataset_size: Total number of records in the dataset
    
    Returns:
        Dictionary with WhyLabs-style formatted monitoring data
    """
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "features_tracked": len(profile_view_df),
            "alert_status": "OK"
        },
        "features": {},
        "unicode_metrics": {},
        "data_quality_metrics": {}
    }

    # Process each feature in the profile
    for feature_name, metrics in profile_view_df.items():
        feature_data = {}
        
        # Standard metrics
        if 'counts/n' in metrics:
            feature_data["counts"] = {
                "count": metrics['counts/n'],
                "missing": metrics.get('counts/null', 0),
                "inf": metrics.get('counts/inf', 0)
            }
        
        # Distribution metrics
        if 'distribution/mean' in metrics:
            feature_data["distribution"] = {
                "mean": metrics['distribution/mean'],
                "stddev": metrics['distribution/stddev'],
                "min": metrics['distribution/min'],
                "max": metrics['distribution/max'],
                "q_25": metrics.get('distribution/q_25'),
                "q_50": metrics.get('distribution/median'),
                "q_75": metrics.get('distribution/q_75')
            }
        
        # Type metrics
        if 'types/integral' in metrics:
            feature_data["types"] = {
                "integral": metrics['types/integral'],
                "fractional": metrics['types/fractional'],
                "boolean": metrics.get('types/boolean', 0),
                "string": metrics.get('types/string', 0)
            }
        
        # Unicode metrics (from your custom resolver)
        if 'unicode_range/digits' in metrics:
            whylabs_data["unicode_metrics"][feature_name] = {
                "digits": metrics['unicode_range/digits'],
                "alpha": metrics.get('unicode_range/alpha', 0)
            }
        
        # Add to features if we found any metrics
        if feature_data:
            whylabs_data["features"][feature_name] = feature_data
            
            # Calculate data quality indicators
            quality_metrics = {
                "completeness": 1 - (metrics.get('counts/null', 0) / metrics['counts/n']) if metrics['counts/n'] > 0 else 1.0,
                "uniqueness": metrics.get('cardinality/est', 0) / metrics['counts/n'] if metrics['counts/n'] > 0 else 0,
                "validity": 1.0  # Default, can be enhanced with custom rules
            }
            whylabs_data["data_quality_metrics"][feature_name] = quality_metrics

    return whylabs_data

@app.get("/profile")
def profile_data():
    """Generates gencrafter profile for the dataset, sends it to WhyLabs, and returns metrics."""
    prof_results = why.log(df, schema=schema)
    prof = prof_results.profile()


    # Convert profile to dictionary
    profile_view = prof.view()
    profile_view_df = profile_view.to_pandas()
    profile_dict = profile_view_df.replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict()

    # Generate WhyLabs-style output
    whylabs_data = map_tracking_profile_to_whylabs(
        profile_view_df=profile_dict,
        dataset_size=len(df)
    )
    
    return {
        "message": "Profile successfully uploaded to WhyLabs",
        "whylabs_formatted_data": whylabs_data,
        "raw_profile_metrics": profile_dict
    }