import json
from collections import defaultdict

# Input and output file paths
blockname = "Gandhwani"
input_file = f"output/span_details-{blockname}.json"
output_file = f"ring_input/ring_details_{blockname}.json"

# Load the input JSON
with open(input_file, "r") as f:
    data = json.load(f)

# Dictionary to hold grouped results
grouped = defaultdict(lambda: {"spans": {}, "meta": {}})

for span_name, span_data in data.items():
    ring = span_data.get("Ring", "UNKNOWN")
    grouped[ring]["spans"][span_name] = span_data

# Now calculate meta info for each ring
for ring, ring_data in grouped.items():
    total_length = 0.0
    category_sums = defaultdict(float)
    total_spans = len(ring_data["spans"])

    for span_name, span_data in ring_data["spans"].items():
        for key, value in span_data.items():
            if isinstance(value, (int, float)):
                category_sums[key] += value
                total_length += value

    ring_data["meta"] = {
        "total_length": total_length,
        "total_spans": total_spans,
        "row_autho": dict(category_sums)
    }

# Write output JSON
with open(output_file, "w") as f:
    json.dump(grouped, f, indent=4)

print(f"✅ Grouped JSON written to {output_file}")
