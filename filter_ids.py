import json
import re

# Load the JSON data
with open('grenoble_stops.json', 'r') as f:
    stops = json.load(f)

# Define the regex pattern
pattern = r'SEM.*'  # Matches "SEM" followed by anything

# Extract matching IDs
matching_ids = []
for stop in stops:
    if 'id' in stop and re.match(pattern, stop['id']):
        matching_ids.append(stop['id'])

# Print results
print(f"Found {len(matching_ids)} matching IDs:")
for id_val in matching_ids:
    print(f"  {id_val}")
