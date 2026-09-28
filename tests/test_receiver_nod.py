import io
import tempfile
import unittest
from unittest.mock import patch

from Receiver_nod import main, process_stream


class ReceiverNodTests(unittest.TestCase):
    def test_reads_zero_values_as_normal_measurement(self):
        out = io.StringIO()
        err = io.StringIO()

        success = process_stream(
            [
                '{"pressure": 0, "temp": 0}\n',
                'END\n',
            ],
            source_name="stdin",
            out=out,
            err=err,
        )

        self.assertIn("empfangene Daten: pressure=0, temp=0", out.getvalue())
        self.assertIn("Abschlusszeile 'END'", out.getvalue())
        self.assertEqual("", err.getvalue())
        self.assertTrue(success)

    def test_end_token_stops_following_measurements(self):
        out = io.StringIO()
        err = io.StringIO()

        success = process_stream(
            [
                '{"pressure": 10, "temp": 20}\n',
                'END\n',
                '{"pressure": 999, "temp": 999}\n',
            ],
            source_name="stdin",
            out=out,
            err=err,
        )

        output = out.getvalue()
        self.assertIn("empfangene Daten: pressure=10, temp=20", output)
        self.assertIn("Abschlusszeile 'END'", output)
        self.assertNotIn("pressure=999", output)
        self.assertEqual("", err.getvalue())
        self.assertTrue(success)

    def test_reports_invalid_json_and_continues(self):
        out = io.StringIO()
        err = io.StringIO()

        success = process_stream(
            [
                '{"pressure": 10, "temp": 20}\n',
                '{invalid json}\n',
                '{"pressure": 11, "temp": 21}\n',
            ],
            source_name="stdin",
            out=out,
            err=err,
        )

        output = out.getvalue()
        self.assertIn("empfangene Daten: pressure=10, temp=20", output)
        self.assertIn("empfangene Daten: pressure=11, temp=21", output)
        self.assertIn("EOF erreicht", output)
        self.assertIn("Ungültiges JSON", err.getvalue())
        self.assertFalse(success)

    def test_reports_missing_or_invalid_fields(self):
        out = io.StringIO()
        err = io.StringIO()

        success = process_stream(
            [
                '{"pressure": 10}\n',
                '{"pressure": "high", "temp": 20}\n',
                '{"pressure": true, "temp": 20}\n',
                '{"pressure": 13, "temp": 23}\n',
            ],
            source_name="stdin",
            out=out,
            err=err,
        )

        error_output = err.getvalue()
        self.assertIn("Fehlende Felder", error_output)
        self.assertIn("müssen numerisch sein", error_output)
        self.assertIn("Zeile 3: Felder müssen numerisch sein: pressure.", error_output)
        self.assertIn("empfangene Daten: pressure=13, temp=23", out.getvalue())
        self.assertFalse(success)

    def test_main_returns_error_code_for_invalid_stdin_input(self):
        fake_stdin = io.StringIO('{"pressure": 1, "temp": 2}\n{bad json}\n')
        fake_stdout = io.StringIO()
        fake_stderr = io.StringIO()

        with patch("sys.stdin", fake_stdin), patch("sys.stdout", fake_stdout), patch("sys.stderr", fake_stderr):
            exit_code = main([])

        self.assertEqual(1, exit_code)
        self.assertIn("empfangene Daten: pressure=1, temp=2", fake_stdout.getvalue())
        self.assertIn("Ungültiges JSON", fake_stderr.getvalue())

    def test_main_reads_optional_file_argument(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = f"{tmp_dir}/measurements.jsonl"
            with open(tmp_path, "w", encoding="utf-8") as tmp_file:
                tmp_file.write('{"pressure": 1001, "temp": 21}\nEND\n')

            fake_stdout = io.StringIO()
            fake_stderr = io.StringIO()
            with patch("sys.stdout", fake_stdout), patch("sys.stderr", fake_stderr):
                exit_code = main(["--file", tmp_path])

        self.assertEqual(0, exit_code)
        self.assertIn("empfangene Daten: pressure=1001, temp=21", fake_stdout.getvalue())
        self.assertIn("Abschlusszeile 'END'", fake_stdout.getvalue())
        self.assertEqual("", fake_stderr.getvalue())

    def test_main_returns_error_for_empty_input(self):
        fake_stdout = io.StringIO()
        fake_stderr = io.StringIO()
        fake_stdin = io.StringIO("")

        with patch("sys.stdin", fake_stdin), patch("sys.stdout", fake_stdout), patch("sys.stderr", fake_stderr):
            exit_code = main([])

        self.assertEqual(1, exit_code)
        self.assertIn("EOF erreicht", fake_stdout.getvalue())
        self.assertIn("Keine gültigen Messdaten verarbeitet", fake_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
