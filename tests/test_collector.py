import sys
import unittest
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cyber_pulse.collector import SystemCollector


class TestSystemCollector(unittest.TestCase):
    def setUp(self):
        self.collector = SystemCollector()

    def tearDown(self):
        self.collector.stop()

    def test_collector_initialization(self):
        self.assertIsNotNone(self.collector)

    def test_get_stats_structure(self):
        stats = self.collector.get_stats()
        self.assertIsInstance(stats, dict)
        expected_keys = ["system", "cpu", "memory", "disks", "network", "processes", "gpus"]
        for key in expected_keys:
            self.assertIn(key, stats, f"Missing key '{key}' in telemetry stats")

    def test_cpu_metrics(self):
        stats = self.collector.get_stats()
        cpu = stats["cpu"]
        self.assertIn("total_percent", cpu)
        self.assertIn("cores_logical", cpu)
        self.assertGreaterEqual(cpu["cores_logical"], 1)
        self.assertGreaterEqual(cpu["total_percent"], 0.0)

    def test_memory_metrics(self):
        stats = self.collector.get_stats()
        mem = stats["memory"]
        self.assertIn("total_gb", mem)
        self.assertIn("percent", mem)
        self.assertGreater(mem["total_gb"], 0.0)
        self.assertGreaterEqual(mem["percent"], 0.0)

    def test_purge_memory_structure(self):
        res = self.collector.purge_memory()
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)
        self.assertIn("freed_mb", res)
        self.assertIn("trimmed_procs", res)
        self.assertIn("message", res)


if __name__ == "__main__":
    unittest.main()
