import csv
import json

# Read data from CSV file
csv_file_path = 'material.csv'
json_file_path = 'material.json'

data = []

with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        # Assuming the CSV file has three columns: type, subtype, material
        entry = {"type": row[0].strip(), "subtype": row[1].strip(), "material": row[2].strip()}
        data.append(entry)

# Write data to JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=2)

print(f'Translation completed. Data written to {json_file_path}')
