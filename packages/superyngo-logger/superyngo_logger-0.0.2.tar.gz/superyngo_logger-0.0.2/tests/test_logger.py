"""
Tests for superyngo_logger package.
"""

import logging
import shutil
import tempfile
import unittest
from pathlib import Path

from superyngo_logger import clean_logs, init_logger


class TestLoggerModule(unittest.TestCase):
    """Test cases for logger_module functions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.log_dir = self.test_dir / "logs"

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_logger_default_params(self):
        """Test init_logger with default parameters."""
        logger = init_logger(log_dir=self.log_dir)
        self.assertIsInstance(logger, logging.Logger)
        self.assertTrue(self.log_dir.exists())

    def test_init_logger_custom_app_name(self):
        """Test init_logger with custom app name."""
        app_name = "test_app"
        logger = init_logger(log_dir=self.log_dir, app_name=app_name)
        self.assertIsInstance(logger, logging.Logger)

        # Check if log file with custom app name exists
        log_files = list(self.log_dir.glob(f"{app_name}_*.log"))
        self.assertTrue(len(log_files) > 0)

    def test_init_logger_multiton_behavior(self):
        """Test that init_logger returns the same instance for the same log_dir."""
        logger1 = init_logger(log_dir=self.log_dir)
        logger2 = init_logger(log_dir=self.log_dir)
        self.assertIs(logger1, logger2)

    def test_clean_logs_invalid_directory(self):
        """Test clean_logs with invalid directory."""
        invalid_dir = self.test_dir / "nonexistent"
        # This should not raise an exception
        clean_logs(invalid_dir, days_count=1)

    def test_clean_logs_no_log_files(self):
        """Test clean_logs with directory containing no log files."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        # Create a non-log file
        (self.log_dir / "not_a_log.txt").touch()

        # This should not raise an exception
        clean_logs(self.log_dir, days_count=1)

        # Non-log file should still exist
        self.assertTrue((self.log_dir / "not_a_log.txt").exists())

    def test_logger_functionality(self):
        """Test basic logger functionality."""
        logger = init_logger(log_dir=self.log_dir, app_name="functional_test")

        # Test logging at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Check if log file was created
        log_files = list(self.log_dir.glob("functional_test_*.log"))
        self.assertTrue(len(log_files) > 0)

        # Check if log file contains content
        log_file = log_files[0]
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Info message", content)
            self.assertIn("Warning message", content)
            self.assertIn("Error message", content)
            self.assertIn("Critical message", content)


class TestPackageImports(unittest.TestCase):
    """Test package imports and version information."""

    def test_import_main_functions(self):
        """Test importing main functions from package."""
        try:
            from superyngo_logger import clean_logs, init_logger

            self.assertTrue(callable(init_logger))
            self.assertTrue(callable(clean_logs))
        except ImportError as e:
            self.fail(f"Failed to import main functions: {e}")

    def test_version_import(self):
        """Test importing version information."""
        try:
            from superyngo_logger import __version__

            self.assertIsInstance(__version__, str)
            self.assertTrue(len(__version__) > 0)
        except ImportError as e:
            self.fail(f"Failed to import version: {e}")


if __name__ == "__main__":
    unittest.main()
