import io
import unittest

from Receiver_nod import process_stream


class ReceiverNodTests(unittest.TestCase):
    def test_reads_zero_values_as_normal_measurement(self):
        out = io.StringIO()
        err = io.StringIO()

        process_stream([
            '{"pressure": 0, "temp": 0}\n',
            'END\n',
        ], source_name="stdin", out=out, err=err)

        self.assertIn("empfangene Daten: pressure=0, temp=0", out.getvalue())
        self.assertIn("Abschlusszeile 'END'", out.getvalue())
        self.assertEqual("", err.getvalue())

    def test_reports_invalid_json_and_continues(self):
        out = io.StringIO()
        err = io.StringIO()

        process_stream([
            '{"pressure": 10, "temp": 20}\n',
            '{invalid json}\n',
            '{"pressure": 11, "temp": 21}\n',
        ], source_name="stdin", out=out, err=err)

        output = out.getvalue()
        self.assertIn("empfangene Daten: pressure=10, temp=20", output)
        self.assertIn("empfangene Daten: pressure=11, temp=21", output)
        self.assertIn("EOF erreicht", output)
        self.assertIn("Ungültiges JSON", err.getvalue())

    def test_reports_missing_or_invalid_fields(self):
        out = io.StringIO()
        err = io.StringIO()

        process_stream([
            '{"pressure": 10}\n',
            '{"pressure": "high", "temp": 20}\n',
            '{"pressure": 13, "temp": 23}\n',
        ], source_name="stdin", out=out, err=err)

        error_output = err.getvalue()
        self.assertIn("Fehlende Felder", error_output)
        self.assertIn("müssen numerisch sein", error_output)
        self.assertIn("empfangene Daten: pressure=13, temp=23", out.getvalue())


if __name__ == "__main__":
    unittest.main()
