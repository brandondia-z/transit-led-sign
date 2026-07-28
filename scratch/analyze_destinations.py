import requests
import json
import os

# Use WMATA Demo API Key
api_key = "e13626d03d8e4c03ac07f95541b3091b"

resp = requests.get(
    "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/All",
    headers={"api_key": api_key}
)
data = resp.json()

mapping = {}
for t in data.get("Trains", []):
    short = t.get("Destination", "")
    full = t.get("DestinationName", "")
    
    if short == "Train" or short == "No Passenger" or not short:
        continue
        
    if short not in mapping:
        mapping[short] = full

print("API Shortening -> Full Name")
print("-" * 40)
for short in sorted(mapping.keys()):
    full = mapping[short]
    if short != full:
        print(f"'{short}' -> '{full}'")

