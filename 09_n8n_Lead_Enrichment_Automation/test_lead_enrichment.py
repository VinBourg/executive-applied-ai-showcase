import unittest

import app


class LeadEnrichmentTests(unittest.TestCase):
    def test_market_alignment_sample_contains_target_markets(self):
        leads = app.load_json(app.LEADS_PATH)
        markets = {(lead["country"], lead["region"]) for lead in leads}
        self.assertIn(("Switzerland", "Zurich"), markets)
        self.assertIn(("France", "Paris"), markets)
        self.assertIn(("United States", "New York"), markets)

    def test_hudson_capital_ops_ranks_as_high_priority(self):
        leads = app.load_json(app.LEADS_PATH)
        evaluated = sorted((app.evaluate_lead(lead) for lead in leads), key=lambda item: item["score"], reverse=True)
        top_names = [lead["company"] for lead in evaluated[:3]]
        self.assertIn("Hudson Capital Ops", top_names)
        hudson = next(lead for lead in evaluated if lead["company"] == "Hudson Capital Ops")
        self.assertEqual(hudson["priority"], "high")

    def test_run_workflow_creates_operational_outputs(self):
        workflow, evaluated = app.run_workflow()
        self.assertTrue(workflow["name"])
        self.assertGreaterEqual(len(evaluated), 5)
        self.assertTrue(app.REPORT_PATH.exists())
        self.assertTrue(app.SCORECARD_PATH.exists())
        self.assertTrue(app.CRM_PAYLOAD_PATH.exists())
        self.assertTrue(app.SEQUENCE_PLAN_PATH.exists())


if __name__ == "__main__":
    unittest.main()
