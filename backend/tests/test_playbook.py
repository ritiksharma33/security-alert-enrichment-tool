import unittest
from services.logic import analyze_threat

class TestSOARPlaybook(unittest.TestCase):
    def test_whitelist_logic(self):
        # Test that Cloudflare is ALWAYS safe
        raw_data = {"ipAddress": "1.1.1.1", "abuseConfidenceScore": 99, "totalReports": 5000}
        risk, _ = analyze_threat(raw_data)
        self.assertEqual(risk, "SAFE")

    def test_critical_threshold(self):
        # Test that 50%+ score is Critical
        raw_data = {"ipAddress": "1.2.3.4", "abuseConfidenceScore": 55, "totalReports": 10}
        risk, _ = analyze_threat(raw_data)
        self.assertEqual(risk, "CRITICAL")

if __name__ == "__main__":
    unittest.main()