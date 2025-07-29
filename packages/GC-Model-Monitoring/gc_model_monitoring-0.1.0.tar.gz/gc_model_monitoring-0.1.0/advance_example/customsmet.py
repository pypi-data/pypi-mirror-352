from fastapi import FastAPI
import pandas as pd
import numpy as np
import requests
import gencrafter as why
from gencrafter.core import  DatasetSchema
from gencrafter.core.resolvers import Resolver
from gencrafter.core.metrics.metrics import Metric, MetricConfig, OperationResult
from gencrafter.core.metrics.metric_components import KllComponent
from gencrafter.core.datatypes import DataType
from gencrafter.core.preprocessing import PreprocessedColumn
import whylogs_sketching as ds
from dataclasses import dataclass
from typing import Dict, Any
from gencrafter.core import DatasetProfile



app = FastAPI()

# Fetch a real-world dataset (Iris dataset from UCI ML repository)
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
COLUMN_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]

@dataclass(frozen=True)
class HistogramMetric(Metric):
    histogram: KllComponent

    @property
    def namespace(self) -> str:
        return "histogram"

    def to_summary_dict(self, cfg) -> Dict[str, Any]:
        if self.histogram.value.get_n() == 0:
            quantiles = [None] * 5
        else:
            quantiles = self.histogram.value.get_quantiles([0.1, 0.25, 0.5, 0.75, 0.9])
        return {
            "n": self.histogram.value.get_n(),
            "max": self.histogram.value.get_max_value(),
            "min": self.histogram.value.get_min_value(),
            "q_10": quantiles[0],
            "q_25": quantiles[1],
            "median": quantiles[2],
            "q_75": quantiles[3],
            "q_90": quantiles[4],
        }

    def columnar_update(self, data: PreprocessedColumn) -> "OperationResult":
        if data.numpy.len > 0:
            for arr in [data.numpy.floats, data.numpy.ints]:
                if arr is not None:
                    self.histogram.value.update(arr)
        return "ok"

    @classmethod
    def zero(cls, config: MetricConfig) -> "HistogramMetric":
        return cls(histogram=KllComponent(ds.kll_doubles_sketch(k=256)))


class TestResolver(Resolver):
    def resolve(self, name: str, why_type: DataType, column_schema) -> Dict[str, Metric]:
        return {"histogram": HistogramMetric.zero(column_schema.cfg)}
# ✅ Define the schema before using it
schema = DatasetSchema(resolvers=TestResolver())

@app.get("/profile")
def profile_data():
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
    df = pd.read_csv(url)

    # Keep only numerical columns
    df = df.select_dtypes(include=["number"])

    # Create dataset profile
    prof = DatasetProfile()

    try:
        prof.track(pandas=df)  # ✅ Track dataframe
    except Exception as e:
        return {"error": f"gencrafter tracking failed: {str(e)}"}

    # Convert profile summary to Pandas DataFrame
    summary = prof.view().to_pandas()

    # ✅ Replace NaN and Infinity values before converting to JSON
    summary = summary.replace({np.nan: None, np.inf: None, -np.inf: None})

    return {"profile_summary": summary.to_dict()}
