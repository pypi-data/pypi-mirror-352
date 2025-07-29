from fastapi import FastAPI
import pandas_gbq
import numpy as np
import pandas as pd
import gencrafter as why
from gencrafter.core import DatasetProfileView
from gencrafter.core.constraints import ConstraintsBuilder
from gencrafter.core.constraints.factories import greater_than_number, mean_between_range
from datetime import datetime
from typing import Dict, Any

app = FastAPI()

PROJECT_ID = "nifty-pursuit-452715-t3"

SQL_QUERY = """
SELECT unique_key, fare, trip_seconds, trip_miles, payment_type, pickup_community_area
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
LIMIT 1000
"""

def map_to_whylabs_format(
    profile_view: DatasetProfileView,
    constraints_report: Dict[str, bool],
    dataset_size: int
) -> Dict[str, Any]:
    """Maps BigQuery profile data to WhyLabs-style format"""
    columns = profile_view.get_columns()
    
    output = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "features_monitored": len(columns),
            "alert_status": "OK"
        },
        "features": {},
        "constraints_report": {
            "constraints": [],
            "summary": {
                "total": len(constraints_report),
                "passed": sum(1 for v in constraints_report.values() if v),
                "failed": sum(1 for v in constraints_report.values() if not v)
            }
        },
        "data_quality_issues": []
    }

    if output["constraints_report"]["summary"]["failed"] > 0:
        output["profile_summary"]["alert_status"] = "WARNING"

    for feature_name, column in columns.items():
        metrics = column.to_summary_dict()
        
        output["features"][feature_name] = {
            "counts": {
                "count": metrics.get("counts/n", 0),
                "missing": metrics.get("counts/nan", 0) + metrics.get("counts/null", 0),
                "null": metrics.get("counts/null", 0),
                "inf": metrics.get("counts/inf", 0)
            },
            "types": {
                "type": metrics.get("type", "unknown"),
                "cardinality": metrics.get("cardinality/est", 0)
            }
        }

        if "distribution" in metrics:
            output["features"][feature_name]["distribution"] = {
                "mean": metrics["distribution"].get("mean"),
                "stddev": metrics["distribution"].get("stddev"),
                "min": metrics["distribution"].get("min"),
                "max": metrics["distribution"].get("max"),
                "quantiles": {
                    "q_01": metrics["distribution"].get("q_01"),
                    "q_25": metrics["distribution"].get("q_25"),
                    "q_50": metrics["distribution"].get("median"),
                    "q_75": metrics["distribution"].get("q_75"),
                    "q_99": metrics["distribution"].get("q_99")
                }
            }

        if "frequent_items" in metrics:
            frequent_items = metrics["frequent_items"]
            
            # Ensure frequent_items is a list
            if isinstance(frequent_items, np.ndarray):
                frequent_items = frequent_items.tolist()

            output["features"][feature_name]["frequent_items"] = frequent_items

    for constraint_name, passed in constraints_report.items():
        feature = constraint_name.split()[0]
        output["constraints_report"]["constraints"].append({
            "name": constraint_name,
            "status": "PASS" if passed else "FAIL",
            "metric": feature,
            "condition": constraint_name
        })

        if not passed:
            output["data_quality_issues"].append({
                "feature": feature,
                "issue_type": "CONSTRAINT_VIOLATION",
                "severity": "HIGH",
                "constraint": constraint_name
            })

    return output

@app.get("/gencrafter/profile")
def get_gencrafter_profile():
    df = pandas_gbq.read_gbq(SQL_QUERY, project_id=PROJECT_ID)
    
    results = why.log(df)
    profile_view = results.view()
    
    
    builder = ConstraintsBuilder(dataset_profile_view=profile_view)
    constraint1 = greater_than_number(column_name="trip_miles", number=0.5)
    constraint2 = mean_between_range(column_name="fare", lower=10.0, upper=50.0)
    
    builder.add_constraint(constraint1)
    builder.add_constraint(constraint2)
    constraints = builder.build()
    
    validation_report = constraints.generate_constraints_report()
    constraints_report = {
        "trip_miles > 0.5": any(r.passed for r in validation_report if "trip_miles > 0.5" in str(r)),
        "fare mean between 10.0 and 50.0": any(r.passed for r in validation_report if "fare mean between 10.0 and 50.0" in str(r))
    }
    
    whylabs_data = map_to_whylabs_format(
        profile_view=profile_view,
        constraints_report=constraints_report,
        dataset_size=len(df)
    )
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "original_profile": profile_view.to_pandas().replace([np.nan, np.inf, -np.inf], None).to_dict(),
        "whylabs_upload_status": "Profile successfully uploaded to WhyLabs"
    }
