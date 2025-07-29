from fastapi import FastAPI, HTTPException
import pandas as pd
import gencrafter as why
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from gencrafter.core import DatasetProfileView
from gencrafter.core.metrics import Metric
from pydantic import BaseModel
import json
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import math
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()


class FeatureStatistics(BaseModel):
    """Model for feature-level statistics with all fields optional"""
    count: Optional[int] = None
    missing: Optional[int] = None
    null: Optional[int] = None
    type: Optional[str] = Field(None, description="Data type from schema")
    inferred_type: Optional[str] = Field(None, description="Automatically detected type")
    mean: Optional[float] = None
    stddev: Optional[float] = None
    min: Optional[Union[float, int]] = None
    max: Optional[Union[float, int]] = None
    quantiles: Optional[Dict[str, float]] = None
    cardinality: Optional[int] = Field(None, description="Number of distinct values")
    frequent_items: Optional[List[Dict[str, Any]]] = None

class ProfileSummary(BaseModel):
    """Model for profile summary"""
    timestamp: str
    profile_type: str
    profile_name: str
    total_observations: int
    features_tracked: int
    ingestion_status: str

class ReferenceMetadata(BaseModel):
    """Model for reference metadata"""
    creation_time: str
    dataset_version: str
    description: str

class WhyLabsFormattedResponse(BaseModel):
    """Complete WhyLabs-compatible response model"""
    profile_summary: ProfileSummary
    features: Dict[str, FeatureStatistics]
    reference_metadata: ReferenceMetadata
    drift_scores: Optional[Dict[str, float]]
    alerts: Optional[List[Dict[str, Any]]]


def _get_metric_value(metric: Optional[Any], attribute: str, default: Any = None) -> Any:
    """Safely get metric values with proper type handling"""
    if metric is None:
        return default
    try:
        value = getattr(metric, attribute, default)
        if hasattr(value, 'value'):
            value = value.value
        return value
    except Exception:
        return default

def _get_type_info(col_profile: Any) -> Dict[str, str]:
    """Improved type detection with actual data inspection"""
    type_metric = col_profile.get_metric("types")
    distribution = col_profile.get_metric("distribution")
    frequent_items = col_profile.get_metric("frequent_items")
    
    # Get values from metrics
    type_name = _get_metric_value(type_metric, "type")
    inferred_type = _get_metric_value(type_metric, "inferred_type")
    
    # If types metric not available, infer from data
    if type_name is None or inferred_type is None:
        if distribution and _get_metric_value(distribution, "mean") is not None:
            return {"type": "numeric", "inferred_type": "integer" if _get_metric_value(distribution, "mean") % 1 == 0 else "float"}
        if frequent_items:
            return {"type": "categorical", "inferred_type": "string"}
    
    return {
        "type": type_name or "unknown",
        "inferred_type": inferred_type or "unknown"
    }

def _get_quantiles(distribution: Optional[Any]) -> Dict[str, float]:
    """Get quantiles with proper validation"""
    if distribution is None or not hasattr(distribution, 'quantiles'):
        return {}
    
    quantiles = {}
    try:
        q_values = distribution.quantiles
        quantile_map = {
            "q_01": 0.01, "q_05": 0.05, "q_25": 0.25,
            "q_50": 0.50, "q_75": 0.75, "q_95": 0.95, "q_99": 0.99
        }
        
        for name, q in quantile_map.items():
            value = q_values.get_value(q)
            if value is not None:
                quantiles[name] = float(value)
    except Exception:
        pass
    
    return quantiles

def _get_frequent_items(frequent_items: Optional[Any]) -> List[Dict[str, Any]]:
    """Extract frequent items with validation"""
    if frequent_items is None:
        return []
    
    try:
        items = []
        for item in frequent_items.to_summary_dict().get("items", [])[:10]:  # Limit to top 10
            items.append({
                "value": str(item.value),
                "estimate": int(item.est)
            })
        return items
    except Exception:
        return []

def map_profile_to_whylabs_format(profile_view: DatasetProfileView, dataset_size: int) -> Dict[str, Any]:
    """Create WhyLabs-compatible output with complete data"""
    features = {}
    
    for col_name in profile_view.get_columns():
        col_profile = profile_view.get_column(col_name)
        
        # Get all relevant metrics
        counts = col_profile.get_metric("counts")
        distribution = col_profile.get_metric("distribution")
        cardinality = col_profile.get_metric("cardinality")
        frequent_items = col_profile.get_metric("frequent_items")
        
        # Build feature statistics
        feature_stats = {
            "count": _get_metric_value(counts, "n"),
            "missing": _get_metric_value(counts, "null"),
            "null": _get_metric_value(counts, "null"),
            **_get_type_info(col_profile),
            "mean": _get_metric_value(distribution, "mean"),
            "stddev": _get_metric_value(distribution, "stddev"),
            "min": _get_metric_value(distribution, "min"),
            "max": _get_metric_value(distribution, "max"),
            "quantiles": _get_quantiles(distribution),
            "cardinality": _get_metric_value(cardinality, "estimate"),
            "frequent_items": _get_frequent_items(frequent_items)
        }
        
        # Clean None values
        features[col_name] = {k: v for k, v in feature_stats.items() if v is not None}
    
    return {
        "profile_summary": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "profile_type": "REFERENCE",
            "profile_name": "hotels_reference",
            "total_observations": dataset_size,
            "features_tracked": len(features),
            "ingestion_status": "COMPLETED"
        },
        "features": features,
        "reference_metadata": {
            "creation_time": datetime.now(timezone.utc).isoformat(),
            "dataset_version": "1.0",
            "description": "Reference profile for hotels dataset"
        },
        "drift_scores": None,
        "alerts": None
    }

@app.get("/log_reference_profile")
async def log_reference_profile():
    try:
        # Load dataset
        csv_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv"
        df = pd.read_csv(csv_url)
        
        # Create profile
        result = why.log(df, dataset_timestamp=datetime.now(timezone.utc))
        profile_view = result.view()
        
        # Generate formatted output
        whylabs_data = map_profile_to_whylabs_format(profile_view, len(df))
        
        
        return {
            "status": "success",
            "data": whylabs_data,
        }
        
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing failed",
                "details": str(e),
                "solution": [
                    "1. Verify dataset URL is accessible",
                    "2. Check WhyLabs credentials",
                    "3. Try smaller dataset if memory issues occur"
                ]
            }
        )
@app.get("/get_gencrafter_json")
async def get_gencrafter_json():
    """Endpoint to get raw gencrafter profile in JSON format"""
    try:
        csv_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv"
        df = pd.read_csv(csv_url)
        
        result = why.log(df, dataset_timestamp=datetime.now(timezone.utc))
        profile_view = result.view()
        
        # Convert profile to JSON
        profile_json = json.loads(profile_view.to_json())
        
        return {
            "status": "success",
            "gencrafter_version": why.__version__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "profile": profile_json
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }