from fastapi import FastAPI
import pandas as pd
import gencrafter as why
from gencrafter.core.resolvers import ResolverSpec, MetricSpec
from gencrafter.core.metrics.condition_count_metric import (
    Condition,
    ConditionCountConfig,
    ConditionCountMetric,
)
from gencrafter.core.schema import DeclarativeSchema
from gencrafter.core.resolvers import STANDARD_RESOLVER
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import os
import numpy as np
import math
import logging
from gencrafter.core.view.column_profile_view import ColumnProfileView
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_float(value: Any) -> Optional[float]:
    """Safely convert any value to float, handling NaN and inf"""
    if value is None:
        return None
    try:
        float_val = float(value)
        if math.isnan(float_val) or math.isinf(float_val):
            return None
        return float_val
    except (ValueError, TypeError):
        return None

def safe_convert(value: Any) -> Any:
    """Recursively convert values to JSON-safe types"""
    if value is None:
        return None
    
    # Handle numpy types
    if isinstance(value, (np.integer, np.int32, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float32, np.float64)):
        return clean_float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return [safe_convert(x) for x in value.tolist()]
    
    # Handle basic types
    if isinstance(value, (int, float, str, bool)):
        if isinstance(value, float):
            return clean_float(value)
        return value
    
    # Handle collections
    if isinstance(value, list):
        return [safe_convert(x) for x in value]
    if isinstance(value, tuple):
        return tuple(safe_convert(x) for x in value)
    if isinstance(value, dict):
        return {str(k): safe_convert(v) for k, v in value.items()}
    
    # Handle objects
    if hasattr(value, 'to_dict'):
        return safe_convert(value.to_dict())
    if hasattr(value, '__dict__'):
        return safe_convert(vars(value))
    
    # Fallback to string representation
    try:
        return str(value)
    except Exception:
        return None

def extract_metric_value(column: ColumnProfileView, metric_name: str, path: str = "") -> Any:
    """Helper to safely extract metric values from column profile"""
    try:
        metric = column.get_metric(metric_name)
        if metric is None:
            return None
            
        summary = metric.to_summary_dict()
        if not path:
            return safe_convert(summary)
        
        value = summary
        for part in path.split('/'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
            if value is None:
                return None
        
        return safe_convert(value)
    except Exception as e:
        logger.debug(f"Error extracting {metric_name}/{path}: {str(e)}")
        return None

def extract_distribution_metrics(column: ColumnProfileView) -> Dict[str, Any]:
    """Extract distribution metrics with proper formatting"""
    return {
        "mean": clean_float(extract_metric_value(column, "distribution", "mean")),
        "stddev": clean_float(extract_metric_value(column, "distribution", "stddev")),
        "min": clean_float(extract_metric_value(column, "distribution", "min")),
        "max": clean_float(extract_metric_value(column, "distribution", "max")),
        "median": clean_float(extract_metric_value(column, "distribution", "median")),
        "q_25": clean_float(extract_metric_value(column, "distribution", "q_25")),
        "q_75": clean_float(extract_metric_value(column, "distribution", "q_75")),
        "n": extract_metric_value(column, "counts", "n"),
    }

def extract_counts_metrics(column: ColumnProfileView) -> Dict[str, Any]:
    """Extract counts metrics"""
    return {
        "total": extract_metric_value(column, "counts", "n") or 0,
        "null": extract_metric_value(column, "counts", "null") or 0,
        "empty": extract_metric_value(column, "counts", "empty") or 0,
        "unique": extract_metric_value(column, "counts", "unique") or 
                 int(extract_metric_value(column, "cardinality", "est") or 0,)
    }

def extract_type_metrics(column: ColumnProfileView) -> Dict[str, Any]:
    """Extract type-related metrics with proper type inference"""
    type_counts = extract_metric_value(column, "types", "counts") or {}
    
    # Determine inferred type based on type counts
    inferred_type = None
    if type_counts:
        # Get all non-zero types
        present_types = {k: v for k, v in type_counts.items() if v > 0}
        if present_types:
            # Get the type with highest count
            inferred_type = max(present_types.items(), key=lambda x: x[1])[0]
            
            # Map gencrafter type names to more readable formats
            type_mapping = {
                "integral": "integer",
                "fractional": "float",
                "boolean": "boolean",
                "string": "string",
                "object": "object",
                "tensor": "tensor"
            }
            inferred_type = type_mapping.get(inferred_type, inferred_type)
    
    return {
        "inferred_type": inferred_type,
        "type_counts": type_counts,
    }
def extract_frequent_items(column: ColumnProfileView) -> List[Dict[str, Any]]:
    """Extract frequent items with proper value conversion"""
    items = extract_metric_value(column, "frequent_items", "frequent_strings") or []
    if not isinstance(items, list):
        return []
    
    frequent_items = []
    for item in items:
        if isinstance(item, dict):
            # Handle dictionary format
            frequent_items.append({
                "value": safe_convert(item.get("value")),
                "estimate": safe_convert(item.get("est")),  # Using 'est' from original
                "rank": len(frequent_items) + 1  # Add rank based on position
            })
        elif hasattr(item, "value"):
            # Handle object format
            frequent_items.append({
                "value": safe_convert(item.value),
                "estimate": safe_convert(getattr(item, "est", None)),
                "rank": len(frequent_items) + 1
            })
    
    return frequent_items

def get_complete_feature_metrics(profile_view, feature_name: str) -> Optional[Dict[str, Any]]:
    """Get complete WhyLabs-style metrics for a single feature"""
    try:
        column = profile_view.get_column(feature_name)
        if not column:
            return None
        
        counts = extract_counts_metrics(column)
        total_count = counts.get("total", 1)
        type_metrics = extract_type_metrics(column)
        
        # Get the summary dict for additional metrics
        summary = column.to_summary_dict()
        
        feature_metrics = {
            "feature_name": feature_name,
            "data_type": type_metrics["inferred_type"],
            "counts": counts,
            "distribution": extract_distribution_metrics(column),
            "cardinality": {
                "unique_count": counts.get("unique"),
                "est_unique_count": extract_metric_value(column, "cardinality", "est"),
            },
            "frequent_items": extract_frequent_items(column),
            "type_metrics": type_metrics,
            "condition_counts": {
                k.split('/')[-1]: safe_convert(v)
                for k, v in summary.items() 
                if k.startswith("condition_count/")
            },
            "data_quality": {
                "missing_percentage": safe_convert(counts.get("null", 0) / total_count if total_count > 0 else 0),
                "constraint_violations": extract_metric_value(column, "constraints", "failed_count") or 0,
            }
        }
        
        # Add string metrics if available
        if "string_length/mean" in summary:
            feature_metrics["string_metrics"] = {
                "length": {
                    "mean": clean_float(summary.get("string_length/mean")),
                    "stddev": clean_float(summary.get("string_length/stddev")),
                    "min": clean_float(summary.get("string_length/min")),
                    "max": clean_float(summary.get("string_length/max")),
                }
            }
        
        return feature_metrics
    except Exception as e:
        logger.error(f"Error processing feature {feature_name}: {str(e)}")
        return None
    
def get_dataset_summary(profile_view, dataset_size: int) -> Dict[str, Any]:
    """Generate WhyLabs-style dataset summary with proper type inference"""
    columns = profile_view.get_columns()
    
    # Calculate dataset-level metrics
    total_null = 0
    total_count = 0
    feature_types = {}
    
    for col_name in columns:
        col = profile_view.get_column(col_name)
        if col:
            counts = extract_counts_metrics(col)
            total_null += counts.get("null", 0)
            total_count += counts.get("total", 0)
            type_metrics = extract_type_metrics(col)
            feature_types[col_name] = type_metrics["inferred_type"]
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "observation_count": dataset_size,
        "total_features": len(columns),
        "data_quality": {
            "missing_value_percentage": safe_convert(total_null / total_count if total_count > 0 else 0),
            "schema_violations": 0,
        },
        "feature_types": feature_types,
    }

def generate_sample_summaries():
    """Generate comprehensive sample data"""
    return pd.DataFrame({
        "summary_text": [
            "The quick brown fox jumps over the lazy dog.",
            "In a comprehensive analysis of market trends...",
            "Researchers discovered a new species...",
            "Major breakthrough in renewable energy...",
            "A detailed examination of historical patterns...",
            "",  # Empty string
            None,  # Null value
            "Another example of a medium-length summary...",
            "The stock market reached record highs today...",
            "Climate change study shows alarming rate..."
        ],
        "sentiment_score": [0.8, 0.2, 0.5, 0.9, 0.3, None, 0.1, 0.6, 0.7, -0.2],
        "category": ["news", "finance", "science", "tech", "finance", None, "news", "finance", "finance", "science"]
    })

@app.get("/log-summaries")
def log_summaries():
    """Endpoint that provides both original and formatted monitoring data"""
    try:
        # Generate or load your data
        df = generate_sample_summaries()
        
        # Define schema with comprehensive metrics
        schema = DeclarativeSchema(STANDARD_RESOLVER)
        
        # Add condition counts for summary length
        nlp_metrics = ResolverSpec(
            column_name="summary_text",
            metrics=[
                MetricSpec(
                    ConditionCountMetric,
                    ConditionCountConfig(
                        conditions={
                            "short_summary": Condition(lambda x: len(x) < 50),
                            "long_summary": Condition(lambda x: len(x) > 100),
                        }
                    ),
                ),
            ],
        )
        schema.add_resolver(nlp_metrics)
        
        # Log the data
        profile_result = why.log(df, schema=schema)
        profile_view = profile_result.view()
        
        # Generate complete WhyLabs-style output
        all_features = {}
        for col in df.columns:
            feature_metrics = get_complete_feature_metrics(profile_view, col)
            if feature_metrics:
                all_features[col] = feature_metrics
        
    
        # Get original profile data (properly serialized)
        original_profile = {}
        for col in df.columns:
            col_profile = profile_view.get_column(col)
            if col_profile:
                try:
                    original_profile[col] = safe_convert(col_profile.to_summary_dict())
                except Exception as e:
                    logger.error(f"Error serializing original profile for {col}: {str(e)}")
                    original_profile[col] = None
        
        # Prepare response
        response = {
            "original_profile": original_profile,
            "formatted_output": {
                "dataset_summary": get_dataset_summary(profile_view, len(df)),
                "feature_metrics": all_features,
            },
            "monitoring_summary": {
                "status": "SUCCESS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
             
            }
        }
        
        return jsonable_encoder(response)
        
    except Exception as e:
        logger.error(f"Error in log_summaries endpoint: {str(e)}", exc_info=True)
        error_response = {
            "error": str(e),
            "traceback": "Check server logs for details",
            "monitoring_summary": {
                "status": "ERROR",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
        
        return jsonable_encoder(error_response)