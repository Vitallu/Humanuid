Import json dev process received
_data(JSON_STRING)..#
data = JSON.loads(JSON_STRING)
pressure = data.get("pressure")
temp = data.get("temp")
print(f"empfangene Daten: (pressur), Temperatur=(temp)")
