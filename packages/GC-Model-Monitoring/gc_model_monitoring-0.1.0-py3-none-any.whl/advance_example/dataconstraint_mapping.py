# whylabs_mapper.py (updated)
from datetime import datetime
from typing import Dict, Any
from gencrafter.core import DatasetProfile
from gencrafter.core.constraints import Constraints

def map_data_constraints_to_whylabs(
    profile_view: DatasetProfile,
    constraints: Constraints,
    dataset_size: int
) -> Dict[str, Any]:
    """
    Updated mapper compatible with current gencrafter constraint reports
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
        # Extract constraint details
        constraint_name = constraint.name
        feature_name = constraint_name.split()[0] if constraint_name else "unknown"
        condition_name = constraint_name.split()[-1] if constraint_name else "condition"
        
        # Add to constraints report
        constraint_data = {
            "name": constraint_name,
            "status": "PASS" if constraint.passed else "FAIL",
            "condition": str(constraint),
            "actual_value": constraint.metric if hasattr(constraint, 'metric') else None,
            "threshold": None  # Will update from constraint object if available
        }
        
        # Try to get threshold from constraint (new gencrafter format)
        if hasattr(constraint, 'constraint'):
            constraint_data["threshold"] = getattr(constraint.constraint, 'threshold', None)
            constraint_data["metric"] = constraint.constraint.metric_name
            
        whylabs_data["constraints_report"]["constraints"].append(constraint_data)
        
        # Process feature-level data
        if feature_name not in whylabs_data["features"]:
            whylabs_data["features"][feature_name] = {
                "constraints": {},
                "condition_metrics": {}
            }
        
        whylabs_data["features"][feature_name]["constraints"][condition_name] = {
            "condition": str(constraint),
            "fail_count": 0 if constraint.passed else 1,
            "status": "PASS" if constraint.passed else "FAIL",
            "actions_triggered": []
        }
        
        # Add condition metrics if available
        feature_metrics = profile_view.get_column(feature_name)
        if feature_metrics and hasattr(feature_metrics, '_metrics'):
            for metric_name, metric in feature_metrics._metrics.items():
                if hasattr(metric, 'to_summary_dict'):
                    metric_summary = metric.to_summary_dict()
                    if 'counts' in metric_summary:
                        whylabs_data["features"][feature_name]["condition_metrics"].update({
                            "total": dataset_size,
                            "failures": metric_summary.get('counts', {}).get('fail', 0),
                            "pass_rate": (dataset_size - metric_summary.get('counts', {}).get('fail', 0)) / dataset_size if dataset_size > 0 else 1.0
                        })
    
    # Add data quality issues for failed constraints
    for constraint in constraints_report:
        if not constraint.passed:
            feature_name = constraint.name.split()[0] if constraint.name else "unknown"
            whylabs_data["data_quality_issues"].append({
                "feature": feature_name,
                "issue_type": "CONSTRAINT_VIOLATION",
                "severity": "HIGH",
                "constraint": str(constraint),
                "actual_value": constraint.metric if hasattr(constraint, 'metric') else None
            })
    
    return whylabs_data