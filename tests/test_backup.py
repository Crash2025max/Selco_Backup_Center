import unittest
import os
import shutil
import tempfile
import zipfile
from src.core.backup import BackupManager

class TestBackupManager(unittest.TestCase):
    def setUp(self):
        self.source_dir = tempfile.mkdtemp()
        self.target_dir = tempfile.mkdtemp()

        # Create some test files
        with open(os.path.join(self.source_dir, "test.txt"), "w") as f:
            f.write("hello world")
        os.makedirs(os.path.join(self.source_dir, "subdir"))
        with open(os.path.join(self.source_dir, "subdir", "subtest.txt"), "w") as f:
            f.write("hello sub")

    def tearDown(self):
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.target_dir)

    def test_create_backup(self):
        manager = BackupManager(self.target_dir)
        success, zip_path = manager.create_backup(self.source_dir, "TestApp", is_auto=True)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(zip_path))
        self.assertIn("TestApp", zip_path)
        self.assertIn("Auto", zip_path)

        # Verify content
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            self.assertIn("test.txt", zipf.namelist())
            self.assertIn("subdir/subtest.txt", zipf.namelist())

    def test_verify_backup(self):
        manager = BackupManager(self.target_dir)
        success, zip_path = manager.create_backup(self.source_dir, "TestApp")
        self.assertTrue(manager.verify_backup(zip_path))

    def test_clean_old_backups(self):
        import time
        manager = BackupManager(self.target_dir)
        # Create 5 mock auto backups
        for i in range(5):
            # Ensure unique filenames by waiting or unique name
            # For test, we can just manually create files to test the cleaning logic
            timestamp = f"2023-10-27_10-00-0{i}"
            filename = f"{manager.pc_name}_TestApp_Auto_{timestamp}.zip"
            zip_path = os.path.join(self.target_dir, filename)
            with open(zip_path, "w") as f: f.write("dummy")
            # simulate time passing for sorting
            os.utime(zip_path, (1000 + i, 1000 + i))

        # Create 1 manual backup (should NOT be deleted)
        manager.create_backup(self.source_dir, "TestApp", is_auto=False)

        manager.clean_old_backups("TestApp", keep_count=2)

        remaining = [f for f in os.listdir(self.target_dir) if "Auto" in f]
        self.assertEqual(len(remaining), 2)

        manual = [f for f in os.listdir(self.target_dir) if "Manuell" in f]
        self.assertEqual(len(manual), 1)

if __name__ == "__main__":
    unittest.main()
