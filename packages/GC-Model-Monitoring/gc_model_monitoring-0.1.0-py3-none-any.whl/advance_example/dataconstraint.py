from fastapi import FastAPI
import pandas as pd
import datetime
from typing import Any
import gencrafter as why
from gencrafter.core.relations import Predicate
from gencrafter.core.metrics.condition_count_metric import Condition
from gencrafter.core.resolvers import STANDARD_RESOLVER
from gencrafter.core.specialized_resolvers import ConditionCountMetricSpec
from gencrafter.core.schema import DeclarativeSchema
from gencrafter.core.constraints.factories import condition_meets, condition_never_meets, condition_count_below
from gencrafter.core.constraints import ConstraintsBuilder
import requests
from fastapi import FastAPI
import pandas as pd
from gencrafter.core import DatasetProfile
from gencrafter.core.constraints import ConstraintsBuilder
from dataconstraint_mapping import map_data_constraints_to_whylabs  # Import the mapper

app = FastAPI()

# Function to check date format
def date_format(x: Any) -> bool:
    date_format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(x, date_format)
        return True
    except ValueError:
        return False

# Alert functions
def pull_andon_cord(validator_name, condition_name: str, value: Any):
    return f"Validator: {validator_name} - Condition {condition_name} failed for value {value} - Pulling andon cord..."

def send_slack_alert(validator_name, condition_name: str, value: Any):
    return f"Validator: {validator_name} - Condition {condition_name} failed for value {value} - Sending slack alert..."



@app.get("/validate")
def validate_data():
    # Your existing data loading and setup
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    column_names = ["age", "workclass", "fnlwgt", "education", "education-num", 
                   "marital-status", "occupation", "relationship", "race", 
                   "sex", "capital-gain", "capital-loss", "hours-per-week", 
                   "native-country", "income"]
    df = pd.read_csv(url, names=column_names, skipinitialspace=True)
    
    # Your existing constraint setup
    schema = DeclarativeSchema(STANDARD_RESOLVER)
    ints_conditions = {"integer_zeros": Condition(Predicate().equals(0))}
    schema.add_resolver_spec("education-num", metrics=[ConditionCountMetricSpec(ints_conditions)])
    
    # Profile and constraints
    profile_view = why.log(df, schema=schema).profile().view()
    builder = ConstraintsBuilder(dataset_profile_view=profile_view)
    builder.add_constraint(condition_count_below("education-num", "integer_zeros", max_count=1))
    constraints = builder.build()
    
    # Generate WhyLabs-style output
    whylabs_data = map_data_constraints_to_whylabs(
        profile_view=profile_view,
        constraints=constraints,
        dataset_size=len(df)
    )
    
    return {
        "whylabs_formatted_data": whylabs_data,
        "original_report": constraints.generate_constraints_report()
    }