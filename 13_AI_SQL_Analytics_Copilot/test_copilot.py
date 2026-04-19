import sqlite3
import unittest

import app


class AnalyticsCopilotTests(unittest.TestCase):
    def setUp(self):
        self.rows = app.load_rows()
        self.connection = sqlite3.connect(":memory:")
        app.setup_database(self.connection, self.rows)

    def tearDown(self):
        self.connection.close()

    def test_detect_intent_routes_supported_questions(self):
        self.assertEqual(
            app.detect_intent("Which accounts need immediate review because revenue is contracting while support pressure stays high?"),
            "risk_review",
        )
        self.assertEqual(
            app.detect_intent("Which industries generate the most revenue but also show operational support pressure?"),
            "segment_pressure",
        )
        self.assertEqual(
            app.detect_intent("Where should we focus expansion efforts based on adoption and pipeline strength?"),
            "growth_focus",
        )

    def test_risk_review_returns_agrinova_first(self):
        spec = app.build_query_spec("risk_review")
        rows = app.fetch_rows(self.connection, spec["sql"])
        self.assertEqual(rows[0]["company_name"], "AgriNova")
        self.assertEqual(rows[0]["recommendation"], "urgent retention review")

    def test_growth_focus_highlights_three_priority_accounts(self):
        spec = app.build_query_spec("growth_focus")
        rows = app.fetch_rows(self.connection, spec["sql"])
        focus = [row["company_name"] for row in rows if row["recommendation"] == "prioritize expansion"]
        self.assertEqual(focus, ["Machina Systems", "AtlasPay", "Swiss Advisory Tech"])

    def test_run_copilot_writes_management_artifacts(self):
        entries = app.run_copilot()
        intents = [entry["intent"] for entry in entries]
        self.assertEqual(intents, ["risk_review", "segment_pressure", "growth_focus"])
        self.assertTrue(app.REPORT_PATH.exists())
        self.assertTrue(app.EXECUTIVE_MEMO_PATH.exists())
        self.assertTrue(app.ROUTE_LOG_PATH.exists())
        self.assertTrue(app.ACTION_QUEUE_PATH.exists())


if __name__ == "__main__":
    unittest.main()
