# stock_mapper.py
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from gencrafter.core import DatasetProfileView

def map_stock_data_to_whylabs(
    profile_view: DatasetProfileView,
    dataset_size: int,
    tickers: list
) -> Dict[str, Any]:
    """
    Maps stock market data profiles to WhyLabs-style format
    """
    profile_data = profile_view.to_summary_dict()
    
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "tickers_monitored": tickers,
            "data_quality_score": 1.0  # Will update based on metrics
        },
        "features": {},
        "time_series_metrics": {
            "timestamps": [],
            "values": {}
        },
        "data_quality_issues": []
    }
    
    # Process each ticker's metrics
    for ticker in tickers:
        if ticker in profile_data["columns"]:
            ticker_metrics = profile_data["columns"][ticker]
            
            whylabs_data["features"][ticker] = {
                "price_metrics": {
                    "last": ticker_metrics.get("distribution", {}).get("mean"),
                    "min": ticker_metrics.get("distribution", {}).get("min"),
                    "max": ticker_metrics.get("distribution", {}).get("max"),
                    "stddev": ticker_metrics.get("distribution", {}).get("stddev"),
                    "percentiles": {
                        "p01": ticker_metrics.get("quantiles", {}).get("0.01"),
                        "p25": ticker_metrics.get("quantiles", {}).get("0.25"),
                        "p50": ticker_metrics.get("quantiles", {}).get("0.50"),
                        "p75": ticker_metrics.get("quantiles", {}).get("0.75"),
                        "p99": ticker_metrics.get("quantiles", {}).get("0.99")
                    }
                },
                "data_quality": {
                    "missing_values": ticker_metrics.get("counts", {}).get("null", 0),
                    "inf_values": ticker_metrics.get("counts", {}).get("inf", 0),
                    "zero_values": ticker_metrics.get("counts", {}).get("zero", 0)
                }
            }
            
            # Check for data quality issues
            if ticker_metrics.get("counts", {}).get("null", 0) > 0:
                whylabs_data["data_quality_issues"].append({
                    "ticker": ticker,
                    "issue_type": "MISSING_VALUES",
                    "severity": "MEDIUM",
                    "count": ticker_metrics["counts"]["null"]
                })
    
    # Calculate overall data quality score
    total_issues = len(whylabs_data["data_quality_issues"])
    whylabs_data["profile_summary"]["data_quality_score"] = max(0, 1 - (total_issues / len(tickers)))
    
    return whylabs_data