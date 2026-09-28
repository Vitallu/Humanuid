# Humanuid

## Receiver_nod.py verwenden

`Receiver_nod.py` erwartet Messdaten als **JSON-Zeilen** mit den numerischen Feldern `pressure` und `temp`.

### 1) Eingabe über `stdin`

```bash
echo '{"pressure": 1013.2, "temp": 22.8}' | python Receiver_nod.py
```

Mehrere Zeilen (interaktiv oder per Pipe) sind möglich.
Beispiel mit Abschluss über EOF:

```bash
python Receiver_nod.py <<'EOF'
{"pressure": 1010, "temp": 21.5}
{"pressure": 1008, "temp": 21.1}
EOF
```

### 2) Optionale Eingabedatei

```bash
python Receiver_nod.py --file messdaten.jsonl
```

Beispiel `messdaten.jsonl`:

```json
{"pressure": 1001, "temp": 19.5}
{"pressure": 0, "temp": 0}
END
```

### Abschlussverhalten

- Die Schleife endet bei **EOF** (z. B. wenn die Pipe/Datei zu Ende ist), oder
- bei einer expliziten Abschlusszeile `END`.
- Die Abschlusszeile wird nach `strip()` geprüft: führende/nachgestellte Leerzeichen werden ignoriert, und der getrimmte Inhalt muss genau `END` sein.
- Nach der Abschlusszeile werden folgende Zeilen nicht mehr verarbeitet.

Wichtig: `temp=0` oder `pressure=0` sind **normale Messwerte** und bedeuten **nicht** automatisch Testende.

### Fehlermeldungen

Bei ungültigem JSON, fehlenden Feldern oder nicht-numerischen Werten gibt das Skript verständliche Fehlermeldungen mit Zeilennummer aus.
Wenn keine gültige Messung verarbeitet wurde (z. B. leere Eingabe), endet das Skript mit Fehlercode `1`.
