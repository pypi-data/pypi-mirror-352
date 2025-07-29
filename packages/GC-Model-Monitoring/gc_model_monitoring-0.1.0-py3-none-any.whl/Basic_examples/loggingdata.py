import gencrafter as why
from gencrafter.core import DatasetProfileView
import numpy as np
import logging
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any
import math
from fastapi.encoders import jsonable_encoder
# Load environment variables

app = FastAPI()
logger = logging.getLogger(__name__)


def serialize_gencrafter_profile(profile_view: DatasetProfileView):
    """Serialize profile with proper handling of all numeric types"""
    try:
        profile_df = profile_view.to_pandas()
        result = {}
        
        for feature_name in profile_df.index:
            feature_stats = profile_df.loc[feature_name].to_dict()
            cleaned_stats = {}
            
            for stat_name, value in feature_stats.items():
                # Handle special float values
                if isinstance(value, float):
                    if math.isinf(value):
                        cleaned_stats[stat_name] = str(value)  # "inf" or "-inf"
                    elif math.isnan(value):
                        cleaned_stats[stat_name] = None
                    else:
                        cleaned_stats[stat_name] = value
                # Handle numpy types
                elif hasattr(value, 'item'):  # Handles numpy types
                    cleaned_stats[stat_name] = value.item()
                else:
                    cleaned_stats[stat_name] = value
            
            result[feature_name] = cleaned_stats
        
        # Use FastAPI's jsonable_encoder for final cleanup
        return jsonable_encoder(result)
        
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        raise HTTPException(status_code=500, detail="Failed to serialize profile")

def map_basic_profile_to_whylabs(profile_view: DatasetProfileView, dataset_size: int) -> Dict[str, Any]:
    """Maps profile to WhyLabs format with proper JSON serialization"""
    try:
        profile_df = profile_view.to_pandas()
        
        # Initialize structure with serializable defaults
        whylabs_data = {
            "profile_summary": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_observations": int(dataset_size),
                "columns_tracked": int(len(profile_df)),
                "alert_status": "OK"
            },
            "features": {},
            "data_quality_metrics": {
                "missing_values": 0,
                "type_mismatches": 0,
                "outliers": 0
            }
        }

        missing_values = 0
        type_mismatches = 0

        for feature_name in profile_df.index:
            feature_stats = profile_df.loc[feature_name].to_dict()
            
            # Create feature entry with safe numeric values
            feature_entry = {
                "counts": {
                    "count": int(feature_stats.get("counts/n", 0)),
                    "missing": int(feature_stats.get("types/null", 0)),
                    "null": int(feature_stats.get("types/null", 0)),
                    "inf": int(feature_stats.get("types/inf", 0))
                },
                "types": {
                    "type": str(feature_stats.get("types/type", "unknown")),
                    "inferred_type": str(feature_stats.get("types/inferred_type", "unknown"))
                },
                "statistics": {}
            }

            # Handle numeric statistics safely
            stats = feature_entry["statistics"]
            for stat in ["mean", "stddev", "min", "max"]:
                val = feature_stats.get(f"distribution/{stat}")
                if val is not None:
                    if isinstance(val, float) and (math.isinf(val) or math.isnan(val)):
                        stats[stat] = None
                    else:
                        stats[stat] = float(val) if val is not None else None

            # Handle quantiles
            quantiles = {
                "q_25": feature_stats.get("distribution/q_25"),
                "q_50": feature_stats.get("distribution/median"),
                "q_75": feature_stats.get("distribution/q_75")
            }
            feature_entry["statistics"]["quantiles"] = {
                k: None if v is None or math.isnan(v) or math.isinf(v) else float(v)
                for k, v in quantiles.items()
            }

            whylabs_data["features"][feature_name] = feature_entry
            
            # Update metrics
            missing_values += int(feature_stats.get("types/null", 0))
            if "types/unexpected" in feature_stats:
                type_mismatches += int(feature_stats["types/unexpected"])

        # Final metrics
        whylabs_data["data_quality_metrics"]["missing_values"] = missing_values
        whylabs_data["data_quality_metrics"]["missing_percentage"] = (
            (missing_values / dataset_size) * 100 if dataset_size > 0 else 0.0
        )
        whylabs_data["data_quality_metrics"]["type_mismatches"] = type_mismatches
        
        # Ensure all values are JSON serializable
        return jsonable_encoder(whylabs_data)
        
    except Exception as e:
        logger.error(f"Mapping error: {e}")
        raise HTTPException(status_code=500, detail="Failed to map profile to WhyLabs format")
# ====================== Helper Functions ======================
def fetch_real_data():
    """Fetch Titanic dataset from GitHub"""
    try:
        url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dataset")


# ====================== API Endpoints ======================
@app.get("/profile-dictionary")
async def profile_dictionary():
    """Endpoint that returns WhyLabs-style formatted profile"""
    try:
        df = fetch_real_data()
        profile = why.log(df).profile()
        profile_view = profile.view()
        

        # Generate WhyLabs-style output
        whylabs_data = map_basic_profile_to_whylabs(
            profile_view=profile_view,
            dataset_size=len(df)
        )
        
        return JSONResponse(content={
            "whylabs_formatted": whylabs_data,
            "raw_profile": serialize_gencrafter_profile(profile_view)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ====================== Main ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)