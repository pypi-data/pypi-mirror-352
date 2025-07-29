from fastapi import FastAPI
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
from gencrafter.core.feature_weights import FeatureWeights
from fastapi.encoders import jsonable_encoder
import os
from datetime import datetime
import numpy as np
import uuid

app = FastAPI()

def generate_whylabs_feature_weights(
    raw_weights: dict,
    model_id: str = "linear_regression",
    timestamp: datetime = None
) -> dict:
    """Generate WhyLabs-compatible feature weights output"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    weights = np.array(list(raw_weights.values()))
    abs_weights = np.abs(weights)
    total_weight = abs_weights.sum()
    
    # Normalize weights to percentage of total
    normalized_weights = (abs_weights / total_weight * 100) if total_weight > 0 else abs_weights
    
    # Calculate weight categories
    mean_weight = np.mean(abs_weights)
    std_weight = np.std(abs_weights)
    
    return {
        "metadata": {
            "modelId": model_id,
            "timestamp": timestamp.isoformat() + "Z",
            "analysisId": str(uuid.uuid4()),
            "tags": ["batch", "regression"],
            "analysisType": "FEATURE_WEIGHTS"
        },
        "featureImportance": {
            "scores": [
                {
                    "featureName": name,
                    "score": float(weight),
                    "absoluteScore": float(abs(weight)),
                    "percentageContribution": float(norm_weight),
                    "direction": "POSITIVE" if weight > 0 else ("NEGATIVE" if weight < 0 else "NEUTRAL"),
                    "significance": (
                        "HIGH" if abs(weight) > mean_weight + std_weight else
                        "MEDIUM" if abs(weight) > mean_weight else
                        "LOW"
                    )
                }
                for name, weight, norm_weight in zip(
                    raw_weights.keys(),
                    weights,
                    normalized_weights
                )
            ],
            "summary": {
                "totalFeatures": len(raw_weights),
                "positiveFeatures": int((weights > 0).sum()),
                "negativeFeatures": int((weights < 0).sum()),
                "neutralFeatures": int((weights == 0).sum()),
                "meanAbsoluteScore": float(mean_weight),
                "maxAbsoluteScore": float(np.max(abs_weights)),
                "scoreDistribution": [
                    {"range": "0-25%", "count": int(((normalized_weights >= 0) & (normalized_weights < 25)).sum())},
                    {"range": "25-50%", "count": int(((normalized_weights >= 25) & (normalized_weights < 50)).sum())},
                    {"range": "50-75%", "count": int(((normalized_weights >= 50) & (normalized_weights < 75)).sum())},
                    {"range": "75-100%", "count": int(((normalized_weights >= 75) & (normalized_weights <= 100)).sum())}
                ]
            }
        }
    }

@app.get("/feature-weights")
def get_feature_weights():
    try:
        # Generate synthetic dataset
        X, y = make_regression(
            n_samples=1000,
            n_features=9,
            n_informative=4,
            random_state=42
        )
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Get raw feature weights
        raw_weights = {
            f"feature_{i}": float(coef)
            for i, coef in enumerate(model.coef_)
        }
        
        # Generate WhyLabs-formatted output
        whylabs_format = generate_whylabs_feature_weights(
            raw_weights=raw_weights,
            model_id="demo_regression_model",
            timestamp=datetime.utcnow()
        )
        
        
        return {
            "raw_weights": raw_weights,
            "whylabs_feature_weights": whylabs_format,
            "message": "Successfully generated feature weights"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to generate feature weights"
        }