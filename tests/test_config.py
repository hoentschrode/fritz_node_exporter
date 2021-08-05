"""Unit tests for config."""
import pytest

from fritz_node_exporter import CONFIG


class TestConfigurationFile:
    """Class covering all testcases for config."""

    def test_file_not_found(self):
        """Test for non existent file."""
        config_file_path = "/this/does/not/exist"
        with pytest.raises(FileNotFoundError):
            CONFIG.load(config_file_path)
