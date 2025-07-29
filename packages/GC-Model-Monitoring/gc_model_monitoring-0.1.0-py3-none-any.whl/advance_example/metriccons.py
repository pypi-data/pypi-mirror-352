from fastapi import FastAPI
import os
import pandas as pd
import gencrafter as why
import requests
from gencrafter.core.constraints import ConstraintsBuilder, MetricConstraint, MetricsSelector
import io
from datetime import datetime
from typing import Dict, Any
from gencrafter.core import DatasetProfile
from gencrafter.core.constraints import Constraints

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ URL of the online dataset (Change to your preferred dataset URL)
DATASET_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"

def load_online_dataset():
    response = requests.get(DATASET_URL)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch dataset. Status code: {response.status_code}")
    
    # Convert to DataFrame
    df = pd.read_csv(io.StringIO(response.text))
    return df

def map_metric_constraints_to_whylabs(
    profile_view: DatasetProfile,
    constraints: Constraints,
    dataset_size: int
) -> Dict[str, Any]:
    """
    Final working version with proper metric value extraction
    """
    constraints_report = constraints.generate_constraints_report()
    
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "constraints_evaluated": len(constraints_report),
            "constraints_passed": sum(1 for r in constraints_report if r.passed),
            "alert_status": "OK"
        },
        "features": {},
        "constraints_report": {
            "constraints": [],
            "summary": {
                "total": len(constraints_report),
                "passed": sum(1 for r in constraints_report if r.passed),
                "failed": sum(1 for r in constraints_report if not r.passed)
            }
        },
        "data_quality_issues": []
    }

    if whylabs_data["constraints_report"]["summary"]["failed"] > 0:
        whylabs_data["profile_summary"]["alert_status"] = "WARNING"
    
    for constraint in constraints_report:
        constraint_name = constraint.name
        feature_name = constraint_name.split()[0] if constraint_name else "unknown"
        
        # Find matching column (case insensitive)
        matching_column = None
        for col in profile_view.get_columns():
            if col.lower() == feature_name.lower():
                matching_column = col
                break
        
        metric_values = {}
        if matching_column:
            column = profile_view.get_column(matching_column)
            if column and hasattr(column, '_metrics') and 'distribution' in column._metrics:
                dist = column._metrics['distribution']
                metric_values = {
                    "min": dist.min if hasattr(dist, 'min') else None,
                    "max": dist.max if hasattr(dist, 'max') else None,
                    "mean": float(dist.mean.value) if hasattr(dist, 'mean') and hasattr(dist.mean, 'value') else None,
                    "stddev": dist.stddev if hasattr(dist, 'stddev') else None,
                    # Quantiles may not be available in all gencrafter versions
                    "q_25": None,
                    "q_50": None,
                    "q_75": None
                }
                
                # Try to get quantiles if available
                if hasattr(dist, 'quantiles'):
                    metric_values.update({
                        "q_25": dist.quantiles.get(0.25),
                        "q_50": dist.quantiles.get(0.5),
                        "q_75": dist.quantiles.get(0.75)
                    })
        
        condition_str = constraint_name.replace("_", " ").title()
        
        # Add to constraints report
        constraint_data = {
            "name": constraint_name,
            "status": "PASS" if constraint.passed else "FAIL",
            "metric": "distribution",
            "condition": condition_str,
            "actual_value": metric_values,
            "threshold": None
        }
        whylabs_data["constraints_report"]["constraints"].append(constraint_data)
        
        # Process feature-level data
        if feature_name not in whylabs_data["features"]:
            whylabs_data["features"][feature_name] = {
                "distribution": metric_values,
                "constraints": {},
                "data_quality": {}
            }
        
        constraint_key = constraint_name.replace(" ", "_").lower()
        whylabs_data["features"][feature_name]["constraints"][constraint_key] = {
            "status": "PASS" if constraint.passed else "FAIL",
            "condition": condition_str,
            "metric_values": metric_values
        }
    
    return whylabs_data
@app.get("/validate_constraints")
def get_validation_report():
    data_df = load_online_dataset()
    
    # Generate profile and constraints
    results = why.log(data_df)
    profile_view = results.view()
    
    # Build constraints
    builder = ConstraintsBuilder(profile_view)
    
    # Age constraints
    if "age" in data_df.columns:
        distribution_age = MetricsSelector(metric_name='distribution', column_name='age')
        builder.add_constraint(MetricConstraint(
            name="Age >= 0",
            condition=lambda x: x.min >= 0,
            metric_selector=distribution_age
        ))
        builder.add_constraint(MetricConstraint(
            name="Age <= 120",
            condition=lambda x: x.max <= 120,
            metric_selector=distribution_age
        ))
    
    # Fare constraints
    if "fare" in data_df.columns:
        distribution_fare = MetricsSelector(metric_name='distribution', column_name='fare')
        builder.add_constraint(MetricConstraint(
            name="Fare >= 0",
            condition=lambda x: x.min >= 0,
            metric_selector=distribution_fare
        ))
    
    constraints = builder.build()
    
    # Generate WhyLabs-style output
    whylabs_data = map_metric_constraints_to_whylabs(
        profile_view=profile_view,
        constraints=constraints,
        dataset_size=len(data_df))
    
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "original_report": [{
            "constraint": r.name,
            "passed": r.passed,
            "failed": not r.passed,
            "summary": str(r)
        } for r in constraints.generate_constraints_report()]
    }