from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
import pandas as pd
import random
import time
import yfinance as yf
import gencrafter as why
from typing import List, Dict, Any
from datetime import datetime, timezone
from gencrafter.core import DatasetSchema
from gencrafter.core.resolvers import StandardResolver
import json
import math

# Custom JSON encoder
class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isinf(obj) or math.isnan(obj):
                return None
            return obj
        return super().default(obj)

app = FastAPI()
app.json_encoder = SafeJSONEncoder

# Directory setup
TMP_PATH = "example_output"
INPUT_PATH = "mock_input"
os.makedirs(TMP_PATH, exist_ok=True)
os.makedirs(INPUT_PATH, exist_ok=True)

# Global control variable
logging_active = False
TICKERS = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"]

def clean_data(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df.replace([float("inf"), float("-inf")], None, inplace=True)
    data_df.fillna(0, inplace=True)
    return data_df

def data_feeder(live_feed=False):
    data = {}
    if live_feed:
        for ticker in TICKERS:
            try:
                stock = yf.Ticker(ticker)
                history = stock.history(period="1d")
                if not history.empty:
                    # Store each ticker's data in a separate column
                    data[f"{ticker}_price"] = history["Close"].iloc[-1]
                    data[f"{ticker}_vol"] = history["Close"].std()  # Add volatility
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
        return clean_data(pd.DataFrame(data, index=[0]))  # Single row with all metrics
    else:
        example_path = os.path.join(INPUT_PATH, "mock_message.json")
        return clean_data(pd.read_json(example_path) if os.path.exists(example_path) else pd.DataFrame())

def read_profile_safely(profile_path):
    try:
        profile = why.read(profile_path)
        view = profile.view()
        return view if view.get_columns() else None
    except Exception as e:
        print(f"Error reading profile {profile_path}: {str(e)}")
        return None

def map_to_whylabs_format(profile_view, dataset_size: int) -> Dict[str, Any]:
    result = {
        "profile_summary": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_observations": dataset_size,
            "tickers_monitored": TICKERS,
            "data_quality_score": 1.0
        },
        "features": {},
        "data_quality_issues": []
    }

    for ticker in TICKERS:
        price_col = f"{ticker}_price"
        vol_col = f"{ticker}_vol"
        
        price_data = profile_view.get_column(price_col).to_summary_dict() if price_col in profile_view.get_columns() else {}
        vol_data = profile_view.get_column(vol_col).to_summary_dict() if vol_col in profile_view.get_columns() else {}
        
        result["features"][ticker] = {
            "price_metrics": {
                "last": price_data.get("distribution", {}).get("mean"),
                "min": price_data.get("distribution", {}).get("min"),
                "max": price_data.get("distribution", {}).get("max"),
                "stddev": price_data.get("distribution", {}).get("stddev"),
                "percentiles": {
                    k: price_data.get("distribution", {}).get(v) 
                    for k, v in [("p01","q_01"),("p25","q_25"),("p50","median"),("p75","q_75"),("p99","q_99")]
                }
            },
            "volatility_metrics": {
                "value": vol_data.get("distribution", {}).get("mean"),
                "stddev": vol_data.get("distribution", {}).get("stddev")
            },
            "data_quality": {
                "missing_values": price_data.get("counts", {}).get("null", 0),
                "inf_values": price_data.get("counts", {}).get("inf", 0),
                "zero_values": price_data.get("counts", {}).get("zero", 0)
            }
        }

    return result

class StockMonitor:

    def consume(self, data_df: pd.DataFrame):
        if not data_df.empty:
            try:
                # Create schema with all expected columns
                columns = [f"{ticker}_price" for ticker in TICKERS] + [f"{ticker}_vol" for ticker in TICKERS]
                schema = DatasetSchema(
                    resolvers=StandardResolver(),
                    types={col: float for col in columns}
                )
                
                profile = why.log(
                    data_df,
                    schema=schema,
                    dataset_timestamp=datetime.now(timezone.utc)
                )
                
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                profile_path = os.path.join(TMP_PATH, f"profile_{timestamp}.bin")
                
                profile.writer("local").write(dest=profile_path)
                profile.writer("whylabs").write()
                
                self.profiles.append(profile_path)
                
                # Update history in memory
                ts = datetime.now(timezone.utc).isoformat()
                self.history["timestamps"].append(ts)
                
                for ticker in TICKERS:
                    price_col = f"{ticker}_price"
                    vol_col = f"{ticker}_vol"
                    
                    if price_col in data_df.columns:
                        self.history["metrics"][ticker]["price"].append(float(data_df[price_col].iloc[0]))
                    else:
                        self.history["metrics"][ticker]["price"].append(None)
                        
                    if vol_col in data_df.columns:
                        self.history["metrics"][ticker]["volatility"].append(float(data_df[vol_col].iloc[0]))
                    else:
                        self.history["metrics"][ticker]["volatility"].append(None)
                
                print(f"Logged data for {len(TICKERS)} tickers")
            except Exception as e:
                print(f"Error logging data: {str(e)}")

app_instance = StockMonitor()

def log_data(live_feed: bool):
    global logging_active
    while logging_active:
        data_df = data_feeder(live_feed)
        app_instance.consume(data_df)
        time.sleep(random.uniform(1, 3))

class StartLoggingRequest(BaseModel):
    live_feed: bool = False

@app.post("/start_logging/")
async def start_logging(request: StartLoggingRequest, background_tasks: BackgroundTasks):
    global logging_active
    if logging_active:
        return {"status": "Already running"}
    logging_active = True
    background_tasks.add_task(log_data, request.live_feed)
    return {"status": "Started logging"}

@app.post("/stop_logging/")
async def stop_logging():
    global logging_active
    logging_active = False
    return {"status": "Stopped logging"}

@app.get("/current_profile")
async def get_current_profile():
    if not app_instance.profiles:
        return {"error": "No profiles available"}
    
    profile_view = read_profile_safely(app_instance.profiles[-1])
    if not profile_view:
        return {"error": "Failed to read profile"}
    
    # Count non-null price columns to get observation count
    row_count = sum(
        1 for ticker in TICKERS 
        if f"{ticker}_price" in profile_view.get_columns() and 
        profile_view.get_column(f"{ticker}_price").to_summary_dict().get("counts", {}).get("n", 0) > 0
    )
    
    return {
        "profile": {
            "columns": {
                col: profile_view.get_column(col).to_summary_dict()
                for col in profile_view.get_columns()
            }
        },
        "whylabs_format": map_to_whylabs_format(profile_view, row_count)
    }

@app.get("/profile_history")
async def get_profile_history():
    return app_instance.history

@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "logging_active": logging_active,
        "profiles_available": len(app_instance.profiles)
    }
    
'''
***pass***

{
   "live_feed": true
} 

as the json 



***how to use***
Clear existing data:

bash
Copy
rm -rf example_output/*
Start the service:

bash
Copy
uvicorn advance_example.logs_rotation:app --reload --port 8082
Start logging:

bash
Copy
curl -X POST http://localhost:8082/start_logging/ \
  -H "Content-Type: application/json" \
  -d '{"live_feed":true}'
Check endpoints:

bash
Copy
# Current profile
curl http://localhost:8082/current_profile

# History
curl http://localhost:8082/profile_history

# Health check
curl http://localhost:8082/health
Stop logging:

bash
Copy
curl -X POST http://localhost:8082/stop_logging/
'''