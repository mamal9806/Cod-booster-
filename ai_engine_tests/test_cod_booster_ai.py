import unittest
from cod_booster_ai import analyze_device, self_test

class EngineTests(unittest.TestCase):
    def test_low_ram_triggers_recommendation(self):
        r = analyze_device({"ram_total_mb": 6000, "ram_available_mb": 300})
        self.assertTrue(any(x["id"] == "memory_cleanup" for x in r["recommendations"]))

    def test_thermal_warning(self):
        r = analyze_device({"battery_temp_c": 46, "thermal_status": "critical"})
        self.assertTrue(any(x["category"] == "thermal" for x in r["recommendations"]))

    def test_network_warning(self):
        r = analyze_device({"ping_ms": 160, "jitter_ms": 35, "packet_loss_percent": 8})
        self.assertIsNotNone(r["network_score"])
        self.assertTrue(any(x["category"] == "network" for x in r["recommendations"]))

    def test_fps_profile(self):
        r = analyze_device({"game_fps_avg": 30, "game_fps_min": 12}, {"target_fps": 60})
        self.assertTrue(any(x["id"] == "fps_profile" for x in r["recommendations"]))

    def test_missing_data_is_unknown(self):
        r = analyze_device({})
        self.assertEqual(r["performance_score"], 0)
        self.assertEqual(r["recommendations"], [])

    def test_self_test(self):
        self.assertTrue(self_test()["ok"])

if __name__ == "__main__":
    unittest.main()
