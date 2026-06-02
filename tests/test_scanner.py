import unittest
import os
import shutil
import tempfile
from src.core.scanner import BiesseScanner

class TestBiesseScanner(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        os.environ["BIESSE_BASE_PATH"] = self.test_dir

        # Create mock program folders
        os.makedirs(os.path.join(self.test_dir, "Osi"))
        with open(os.path.join(self.test_dir, "Osi", "Osi.exe"), "w") as f:
            f.write("mock content")

        os.makedirs(os.path.join(self.test_dir, "LPrint"))
        with open(os.path.join(self.test_dir, "LPrint", "LPrint.exe"), "w") as f:
            f.write("mock content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "BIESSE_BASE_PATH" in os.environ:
            del os.environ["BIESSE_BASE_PATH"]

    def test_scan_finds_installed_programs(self):
        scanner = BiesseScanner()
        results = scanner.scan()

        self.assertTrue(results["OSI"]["installed"])
        self.assertTrue(results["LPrint"]["installed"])
        self.assertFalse(results["Bopti"]["installed"])
        self.assertFalse(results["Optiplanning"]["installed"])
        self.assertFalse(results["LEdit"]["installed"])

    def test_pc_name_is_not_empty(self):
        scanner = BiesseScanner()
        pc_name = scanner.get_pc_name()
        self.assertTrue(len(pc_name) > 0)

if __name__ == "__main__":
    unittest.main()
