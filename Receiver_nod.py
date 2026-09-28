import json

JSON_STRING = '{"pressure": 0, "temp": 0}'
data = json.loads(JSON_STRING)
pressure = data.get("pressure")
temp = data.get("temp")
print(f"empfangene Daten: pressure={pressure}, temp={temp}")
