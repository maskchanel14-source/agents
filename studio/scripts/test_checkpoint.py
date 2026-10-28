import unittest

from checkpoint import append_once, render_row, validate_snapshot

SNAPSHOT = {
    "product": "ScopeReply",
    "buyer": "Web designers",
    "channel": "Reddit",
    "status": "validating",
    "commitments": 0,
    "paid_customers": 0,
    "collected_cents": 0,
    "outreach_started_at": None,
    "hard_stop_at": "2026-10-30T21:05:00Z",
    "decision": "No outreach yet",
    "skill_used": "before-you-build",
    "snapshot_at": "2026-10-29T00:05:00Z",
}
TABLE = "# Log\n\n| Time | Product |\n|---|---|\n| existing | row |\n\n## Notes\n"


class CheckpointTests(unittest.TestCase):
    def test_truthful_row(self):
        row = render_row(SNAPSHOT)
        self.assertIn("Not posted. Selected: Reddit", row)
        self.assertIn("0/3 commitments", row)
        self.assertIn("| 0.00 |", row)

    def test_idempotent_and_order(self):
        row = render_row(SNAPSHOT)
        once = append_once(TABLE, row)
        self.assertEqual(append_once(once, row), once)
        self.assertLess(once.index("existing"), once.index("Not posted"))
        self.assertIn("## Notes", once)

    def test_rejects_fabricated_shape(self):
        for key, value in [
            ("commitments", -1),
            ("paid_customers", True),
            ("collected_cents", 1.2),
            ("decision", "fake\nrow"),
            ("snapshot_at", "2026-10-29"),
        ]:
            with self.assertRaises((ValueError, TypeError)):
                validate_snapshot({**SNAPSHOT, key: value})
        with self.assertRaises(ValueError):
            validate_snapshot({})


if __name__ == "__main__":
    unittest.main()
