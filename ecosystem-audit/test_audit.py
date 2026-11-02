"""Regression tests for read-only gap scanner; no database or credentials required."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

path = Path(__file__).resolve().with_name("audit.py")
spec = importlib.util.spec_from_file_location("ssag_audit", path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class GapDetectionTests(unittest.TestCase):
    def setUp(self):
        audit.FINDINGS.clear()

    def test_zero_record_pipeline_is_reported(self):
        with patch.object(audit, "table_exists", return_value=True), \
             patch.object(audit, "columns", return_value={"id"}), \
             patch.object(audit, "scalar", return_value=0):
            audit.count_check(None, "clientflow", "NO_LEADS_RECORDED",
                              "select count(*) from leads", {"leads": {"id"}},
                              "P1", alert_when_zero=True)
        self.assertEqual(audit.FINDINGS[0]["count"], 0)

    def test_nonzero_pipeline_does_not_raise_zero_record_alert(self):
        with patch.object(audit, "table_exists", return_value=True), \
             patch.object(audit, "columns", return_value={"id"}), \
             patch.object(audit, "scalar", return_value=4):
            audit.count_check(None, "nextchapter", "NO_ORDERS_RECORDED",
                              "select count(*) from orders", {"orders": {"id"}},
                              "P1", alert_when_zero=True)
        self.assertFalse(audit.FINDINGS)

    def test_missing_contact_stamp_is_positive_count_alert(self):
        with patch.object(audit, "table_exists", return_value=True), \
             patch.object(audit, "columns", return_value={"id"}), \
             patch.object(audit, "scalar", return_value=2):
            audit.count_check(None, "sentinel", "MISSING_CONTACT_STAMP",
                              "select count(*) from leads", {"leads": {"id"}})
        self.assertEqual(audit.FINDINGS[0]["count"], 2)

    def test_missing_schema_is_not_silent(self):
        with patch.object(audit, "table_exists", return_value=False):
            audit.count_check(None, "dispatch", "CALL_WITHOUT_START",
                              "select count(*) from calls", {"calls": {"id"}})
        self.assertEqual(audit.FINDINGS[0]["severity"], "P0")


if __name__ == "__main__":
    unittest.main()
