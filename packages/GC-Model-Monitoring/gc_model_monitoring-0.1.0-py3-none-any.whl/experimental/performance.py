from fastapi import FastAPI
import pandas as pd
import numpy as np
import gencrafter as why
from gencrafter.core.schema import DatasetSchema
from gencrafter.core.segmentation_partition import segment_on_column
from gencrafter.experimental.performance_estimation.estimators import AccuracyEstimator
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Dict, Any, List

app = FastAPI()

# Load Titanic dataset from an online source
dataset_url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df = pd.read_csv(dataset_url)

# Preprocessing
df = df[['PassengerId', 'Pclass', 'Age', 'Fare', 'Survived']]
df.dropna(inplace=True)
df['output_survived'] = df['Survived']
df['output_prediction'] = np.where(df['Fare'] > df['Fare'].median(), 1, 0)

reference_df = df.copy()

class UploadRequest(BaseModel):
    org_id: str
    dataset_id: str
    api_key: str
def get_baseline_stats(df):
    return {
        "Fare": {
            "median": df["Fare"].median(),
            "mean": df["Fare"].mean()
        },
        **df.head().to_dict()  # Includes the sample data you showed
    }

def map_performance_to_whylabs(
    reference_profile,
    estimator,
    perturbed_profiles,
    accuracy_results,
    dataset_size,
    baseline_data: dict
) -> Dict[str, Any]:
    """Enhanced performance mapper for Titanic dataset"""
    segments = reference_profile.segments() if hasattr(reference_profile, 'segments') else []
    
    # Calculate key metrics
    avg_accuracy_drop = sum(abs(r["real_accuracy"] - r["estimated_accuracy"]) 
                          for r in accuracy_results) / len(accuracy_results) if accuracy_results else 0
    
    # Extract baseline stats
    fare_stats = {
        "median": baseline_data["Fare"]["median"],
        "mean": baseline_data["Fare"]["mean"],
        "threshold_used": baseline_data["Fare"]["median"]  # Your prediction threshold
    }
    
    # Build the output structure
    result = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": dataset_size,
            "dataset_stats": {
                "survival_rate": sum(baseline_data["Survived"].values()) / len(baseline_data["Survived"]),
                "prediction_threshold": fare_stats["threshold_used"],
                "class_distribution": {
                    str(cls): sum(1 for v in baseline_data["Pclass"].values() if v == cls)
                    for cls in set(baseline_data["Pclass"].values())
                }
            }
        },
        "performance_metrics": {
            "reference_accuracy": estimator.reference_accuracy,
            "estimation_method": str(estimator.__class__.__name__),
            "fare_threshold_analysis": fare_stats
        },
        "performance_over_time": [{
            "day_offset": day,
            "estimated_accuracy": result["estimated_accuracy"],
            "actual_accuracy": result["real_accuracy"],
            "accuracy_gap": result["real_accuracy"] - result["estimated_accuracy"],
            "confidence_band": 0.95  # Could be calculated from variance
        } for day, result in enumerate(accuracy_results)],
        "segmented_analysis": {
            str(segment): {
                "reference_accuracy": estimator.estimate(reference_profile.segment(segment)).accuracy,
                "sample_size": reference_profile.segment(segment).count(),
                "survival_rate": sum(
                    1 for i, survived in enumerate(baseline_data["output_survived"].values()) 
                    if baseline_data["Pclass"][str(i)] == int(segment.split("=")[1])
                ) / reference_profile.segment(segment).count()
            }
            for segment in segments
        } if segments else {},
        "data_quality_alerts": [{
            "type": "ACCURACY_DROP",
            "severity": "HIGH" if avg_accuracy_drop > 0.15 else "MEDIUM",
            "metric": "accuracy_gap",
            "value": avg_accuracy_drop,
            "suggested_actions": [
                "Verify fare distribution changes",
                "Check for data drift in passenger demographics"
            ]
        }] if avg_accuracy_drop > 0.1 else []
    }
    
    return result

@app.get("/baseline")
def get_baseline():
    return reference_df.head().to_dict()

def log_dataset(df, labeled=True):
    segmented_schema = DatasetSchema(segments=segment_on_column("Pclass"))
    if labeled:
        return why.log_classification_metrics(
            df,
            target_column="output_survived",
            prediction_column="output_prediction",
            schema=segmented_schema,
            log_full_data=True
        )
    else:
        return why.log(df, schema=segmented_schema)

reference_results = log_dataset(reference_df, labeled=True)

# Simulate perturbed datasets
perturbed_dfs = [reference_df.copy() for _ in range(7)]
for df in perturbed_dfs:
    df['Age'] = df['Age'] * np.random.uniform(0.9, 1.1)
    df['Fare'] = df['Fare'] * np.random.uniform(0.9, 1.1)

perturbed_results_list = [log_dataset(df, labeled=False) for df in perturbed_dfs]
estimator = AccuracyEstimator(reference_result_set=reference_results)
@app.get("/accuracy")
def get_accuracy():
    # Initialize results with Python native types
    results = []
    
    # Calculate reference accuracy (convert to float)
    reference_accuracy = float((reference_df['output_survived'] == reference_df['output_prediction']).mean())
    
    # Calculate accuracy metrics for each perturbed dataset
    for day, perturbed_df in enumerate(perturbed_dfs):
        # Calculate REAL accuracy for THIS perturbed dataset
        real_acc = float((perturbed_df['output_survived'] == perturbed_df['output_prediction']).mean())
        
        # Calculate accuracy by class with native Python types
        accuracy_by_class = {}
        for pclass in [1, 2, 3]:
            class_df = perturbed_df[perturbed_df['Pclass'] == pclass]
            if len(class_df) > 0:
                accuracy_by_class[f"class_{pclass}"] = {
                    "accuracy": float((class_df['output_survived'] == class_df['output_prediction']).mean()),
                    "count": int(len(class_df))  # Convert to native int
                }
        
        # Simple estimation using reference accuracy with some variation
        estimated_acc = float(reference_accuracy * np.random.uniform(0.95, 1.05))
        
        results.append({
            "day": int(day),  # Ensure day is native int
            "real_accuracy": real_acc,
            "estimated_accuracy": estimated_acc,
            "accuracy_by_class": accuracy_by_class,
            "accuracy_difference": float(real_acc - estimated_acc)
        })
    
    # Generate WhyLabs-style output with all native Python types
    whylabs_data = {
        "profile_summary": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_observations": int(len(reference_df)),
            "class_distribution": {
                str(pclass): int((reference_df['Pclass'] == pclass).sum())  # Convert to native int
                for pclass in [1, 2, 3]
            }
        },
        "performance_metrics": {
            "reference_accuracy": reference_accuracy,
            "prediction_threshold": float(reference_df['Fare'].median())  # Convert to float
        },
        "performance_over_time": {
            "overall": [{
                "day": r["day"],
                "real_accuracy": r["real_accuracy"],
                "estimated_accuracy": r["estimated_accuracy"]
            } for r in results],
            "by_class": {
                f"class_{pclass}": [{
                    "day": r["day"],
                    "accuracy": r["accuracy_by_class"].get(f"class_{pclass}", {}).get("accuracy"),
                    "count": r["accuracy_by_class"].get(f"class_{pclass}", {}).get("count")
                } for r in results]
                for pclass in [1, 2, 3]
            }
        },
        "data_quality_alerts": []
    }
    
    # Calculate average accuracy drop with proper type conversion
    if results:
        avg_drop = float(sum(abs(r["accuracy_difference"]) for r in results) / len(results))
        if avg_drop > 0.1:
            whylabs_data["data_quality_alerts"].append({
                "type": "ACCURACY_DROP",
                "severity": "HIGH" if avg_drop > 0.15 else "MEDIUM",
                "value": avg_drop,
                "suggested_actions": [
                    "Check fare distribution changes",
                    "Verify passenger demographics"
                ]
            })
    
    return whylabs_data
