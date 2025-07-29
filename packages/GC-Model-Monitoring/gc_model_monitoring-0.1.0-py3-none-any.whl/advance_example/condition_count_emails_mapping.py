import json
import requests

# 🔹 Replace with your actual FastAPI endpoint
FASTAPI_URL = "http://127.0.0.1:8000/profile/emails"

# Fetch data from FastAPI
response = requests.get(FASTAPI_URL)

if response.status_code == 200:
    gencrafter_json = response.json()  # Convert response to JSON
    print("✅ API Response Received")
else:
    print(f"❌ API Request Failed: {response.status_code}")
    exit()

# 🔹 Define gencrafter-to-WhyLabs mapping
mapping_schema = {
    "cardinality/est": "Cardinality Estimate",
    "cardinality/lower_1": "Cardinality Lower Bound",
    "cardinality/upper_1": "Cardinality Upper Bound",
    "condition_count/between10and50": "Condition Count (Between 10 and 50)",
    "condition_count/not_42": "Condition Count (Not 42)",
    "condition_count/total": "Total Condition Count",
    "counts/n": "Total Count",
    "counts/null": "Null Count",
    "counts/nan": "NaN Count",
    "distribution/max": "Max",
    "distribution/mean": "Mean",
    "distribution/median": "Median",
    "distribution/min": "Min",
    "distribution/stddev": "Standard Deviation",
    "distribution/q_25": "25th Percentile",
    "distribution/q_75": "75th Percentile",
    "ints/max": "Integer Max",
    "ints/min": "Integer Min",
    "types/boolean": "Boolean Count",
    "types/fractional": "Fractional Count",
    "types/integral": "Integral Count",
}

# 🔹 Detect column names dynamically
column_names = list(next(iter(gencrafter_json.values()), {}).keys())

# 🔹 Initialize structured output dynamically
mapped_data = {"columns": {col: {} for col in column_names}}

# 🔹 Populate mapped structure
for key, values in gencrafter_json.items():
    if key in mapping_schema:
        new_key = mapping_schema[key]  # Get mapped name
        for col in column_names:
            mapped_data["columns"][col][new_key] = values.get(col, None)  # Avoid KeyErrors

# 🔹 Convert to JSON format
mapped_json = json.dumps(mapped_data, indent=4)

# 🔹 Save or print the output
with open("mapped_whylabs.json", "w") as f:
    f.write(mapped_json)

print("✅ Mapped JSON saved as 'mapped_whylabs.json'")
print("🔹 Mapped Output Preview:\n", mapped_json)
