"""Tests for config migration and multi-provider support."""
import os
import stat
import json
import pytest
from unittest.mock import patch, MagicMock
from imggen.config import (
    load_config,
    save_config,
    get_api_keys,
    get_api_key_for_provider,
    get_config_dir,
    DEFAULT_PROVIDER,
)


class TestConfigMigration:
    """Test migration from old to new config format."""

    def test_migrate_old_format_to_new(self, tmp_path):
        """Test migrating old single-key format to new multi-key format."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        # Write old format
        old_config = {"api_key": "old-google-key"}
        with open(config_file, "w") as f:
            json.dump(old_config, f)

        # Mock get_config_file to use temp directory
        with patch("imggen.config.get_config_file", return_value=config_file):
            config = load_config()

            # Should have migrated to new format
            assert "api_keys" in config
            assert config["api_keys"]["google"] == "old-google-key"
            assert config["default_provider"] == "google"

            # Verify file was updated
            with open(config_file) as f:
                saved_config = json.load(f)
                assert saved_config["api_keys"]["google"] == "old-google-key"

    def test_new_format_stays_unchanged(self, tmp_path):
        """Test that new format is not modified."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        # Write new format
        new_config = {
            "api_keys": {"google": "google-key", "openai": "openai-key"},
            "default_provider": "openai",
        }
        with open(config_file, "w") as f:
            json.dump(new_config, f)

        # Mock get_config_file
        with patch("imggen.config.get_config_file", return_value=config_file):
            config = load_config()

            # Should remain unchanged
            assert config["api_keys"]["google"] == "google-key"
            assert config["api_keys"]["openai"] == "openai-key"
            assert config["default_provider"] == "openai"


class TestMultiProviderConfig:
    """Test multi-provider configuration."""

    def test_get_api_keys(self, tmp_path):
        """Test getting all API keys."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        config = {
            "api_keys": {"google": "google-key", "openai": "openai-key"},
            "default_provider": "openai",
        }
        with open(config_file, "w") as f:
            json.dump(config, f)

        with patch("imggen.config.get_config_file", return_value=config_file):
            keys = get_api_keys()
            assert keys["google"] == "google-key"
            assert keys["openai"] == "openai-key"

    def test_get_api_key_for_existing_provider(self, tmp_path):
        """Test getting API key for provider that exists."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        config = {"api_keys": {"google": "google-key", "openai": "openai-key"}}
        with open(config_file, "w") as f:
            json.dump(config, f)

        with patch("imggen.config.get_config_file", return_value=config_file):
            google_key = get_api_key_for_provider("google")
            assert google_key == "google-key"

            openai_key = get_api_key_for_provider("openai")
            assert openai_key == "openai-key"

    def test_get_api_key_for_missing_provider_prompts(self, tmp_path):
        """Test that missing API key prompts user."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        config = {"api_keys": {}}
        with open(config_file, "w") as f:
            json.dump(config, f)

        with patch("imggen.config.get_config_file", return_value=config_file):
            with patch("imggen.config.getpass", return_value="new-key"):
                key = get_api_key_for_provider("google")
                assert key == "new-key"

                # Verify it was saved
                with open(config_file) as f:
                    saved = json.load(f)
                    assert saved["api_keys"]["google"] == "new-key"

    def test_get_api_key_empty_input_exits(self, tmp_path):
        """Test that empty API key input exits."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        config = {"api_keys": {}}
        with open(config_file, "w") as f:
            json.dump(config, f)

        with patch("imggen.config.get_config_file", return_value=config_file):
            with patch("imggen.config.getpass", return_value=""):
                with pytest.raises(SystemExit):
                    get_api_key_for_provider("google")


class TestFilePermissions:
    """Test config file and directory permissions."""

    def test_config_directory_permissions(self, tmp_path, monkeypatch):
        """Test config directory is created with 0o700 permissions."""
        config_home = tmp_path / ".config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

        config_dir = get_config_dir()

        # Check directory exists
        assert config_dir.exists()

        # Check permissions are 0o700 (rwx------)
        dir_mode = os.stat(config_dir).st_mode
        permissions = stat.S_IMODE(dir_mode)
        assert permissions == 0o700

    def test_config_file_permissions(self, tmp_path):
        """Test config file is created with 0o600 permissions."""
        config_dir = tmp_path / ".config" / "imggen"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.json"

        config = {"api_keys": {"openai": "test-key"}}

        with patch("imggen.config.get_config_file", return_value=config_file):
            save_config(config)

            # Check file exists
            assert config_file.exists()

            # Check permissions are 0o600 (rw-------)
            file_mode = os.stat(config_file).st_mode
            permissions = stat.S_IMODE(file_mode)
            assert permissions == 0o600
