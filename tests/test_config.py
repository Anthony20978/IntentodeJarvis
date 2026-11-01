import os
import unittest
from pathlib import Path
from unittest.mock import patch
from src.jarvis import config
class ConfigTests(unittest.TestCase):
    def test_windows_data_directory(self):
        with patch.object(config, "SYSTEM", "Windows"):
            with patch.dict(
                os.environ,
                {"LOCALAPPDATA": "C:/Users/Test/AppData/Local"}
            ):
                result = config.get_data_directory()
        self.assertEqual(
            result,
            Path("C:/Users/Test/AppData/Local/JARVIS")
        )
    def test_windows_fallback_directory(self):
        with patch.object(config, "SYSTEM", "Windows"):
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(
                    config.Path, "home",
                    return_value=Path("C:/Users/Test")
                ):
                    result = config.get_data_directory()

        self.assertEqual(
            result,
            Path("C:/Users/Test/AppData/Local/JARVIS")
        )
    def test_macos_data_directory(self):
        with patch.object(config, "SYSTEM", "Darwin"):
            result = config.get_data_directory()
        self.assertEqual(
            result,
            Path.home() / "Library" / "Application Support" / "JARVIS"
        )
    def test_linux_data_directory(self):
        with patch.object(config, "SYSTEM", "Linux"):
            with patch.dict(
                os.environ,
                {"XDG_DATA_HOME": "/home/test/.local/share"}
            ):
                result = config.get_data_directory()
        self.assertEqual(
            result,
            Path("/home/test/.local/share/jarvis")
        )
    def test_linux_fallback_directory(self):
        with patch.object(config, "SYSTEM", "Linux"):
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(
                    config.Path, "home",
                    return_value=Path("/home/test")
                ):
                    result = config.get_data_directory()

        self.assertEqual(
            result,
            Path("/home/test/.local/share/jarvis")
        )
if __name__ == "__main__":
    unittest.main()