import argparse
import json
import sys
from typing import Iterable, Optional, TextIO


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_measurement(line: str, line_number: int) -> dict:
    try:
        data = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Zeile {line_number}: Ungültiges JSON ({exc.msg})."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Zeile {line_number}: Erwartet JSON-Objekt mit 'pressure' und 'temp'."
        )

    missing = [field for field in ("pressure", "temp") if field not in data]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Zeile {line_number}: Fehlende Felder: {missing_text}.")

    pressure = data["pressure"]
    temp = data["temp"]
    invalid = [
        name
        for name, value in (("pressure", pressure), ("temp", temp))
        if not _is_number(value)
    ]
    if invalid:
        invalid_text = ", ".join(invalid)
        raise ValueError(f"Zeile {line_number}: Felder müssen numerisch sein: {invalid_text}.")

    return {"pressure": pressure, "temp": temp}


def process_stream(
    stream: Iterable[str],
    source_name: str,
    out: TextIO,
    err: TextIO,
    end_token: str = "END",
) -> None:
    for line_number, raw_line in enumerate(stream, start=1):
        line = raw_line.strip()
        if not line:
            continue

        if line == end_token:
            print(
                f"Eingabe beendet: Abschlusszeile '{end_token}' erkannt ({source_name}, Zeile {line_number}).",
                file=out,
            )
            return

        try:
            data = parse_measurement(line, line_number)
        except ValueError as exc:
            print(f"Fehler: {exc}", file=err)
            continue

        print(
            f"empfangene Daten: pressure={data['pressure']}, temp={data['temp']}",
            file=out,
        )

    print(f"Eingabe beendet: EOF erreicht ({source_name}).", file=out)


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Liest Messdaten als JSON-Zeilen von stdin oder optional aus einer Datei. "
            "Jede Zeile muss ein Objekt mit numerischen Feldern 'pressure' und 'temp' enthalten."
        )
    )
    parser.add_argument(
        "--file",
        dest="file_path",
        help="Optionale Datei mit JSON-Zeilen (eine Messung pro Zeile).",
    )
    args = parser.parse_args(argv)

    if args.file_path:
        try:
            with open(args.file_path, "r", encoding="utf-8") as file_obj:
                process_stream(file_obj, source_name=args.file_path, out=sys.stdout, err=sys.stderr)
        except OSError as exc:
            print(f"Fehler: Datei kann nicht gelesen werden: {exc}", file=sys.stderr)
            return 1
    else:
        process_stream(sys.stdin, source_name="stdin", out=sys.stdout, err=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
