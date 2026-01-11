"""Tests for image generation and file collision detection."""
import pytest


class TestFileCollisionDetection:
    """Tests for file collision detection."""

    def test_check_file_collisions_no_collision(self, tmp_path):
        """Test collision detection when no files exist."""
        from imggen.generator import check_file_collisions

        has_collision, collisions = check_file_collisions(str(tmp_path), 4)
        assert has_collision is False
        assert collisions == []

    def test_check_file_collisions_with_collision(self, tmp_path):
        """Test collision detection when files exist."""
        from imggen.generator import check_file_collisions

        # Create some files
        (tmp_path / "imggen_001.png").touch()
        (tmp_path / "imggen_002.png").touch()

        has_collision, collisions = check_file_collisions(str(tmp_path), 4)
        assert has_collision is True
        assert "imggen_001.png" in collisions
        assert "imggen_002.png" in collisions
        assert "imggen_003.png" not in collisions

    def test_check_file_collisions_partial_collision(self, tmp_path):
        """Test when only some files exist."""
        from imggen.generator import check_file_collisions

        (tmp_path / "imggen_003.png").touch()

        has_collision, collisions = check_file_collisions(str(tmp_path), 4)
        assert has_collision is True
        assert "imggen_003.png" in collisions
        assert "imggen_001.png" not in collisions

    def test_format_collision_error(self):
        """Test collision error message formatting."""
        from imggen.generator import format_collision_error

        collisions = ["imggen_001.png", "imggen_002.png"]
        message = format_collision_error(collisions, "./output")

        assert "Error: File collision detected" in message
        assert "imggen_001.png" in message
        assert "imggen_002.png" in message
        assert "No API calls were made" in message


class TestModelParameter:
    """Test model parameter passing through generation flow."""

    def test_generate_single_image_passes_model_to_provider(self, tmp_path):
        """Test that generate_single_image passes model to provider."""
        from imggen.generator import generate_single_image
        from unittest.mock import MagicMock, patch

        mock_provider = MagicMock()
        mock_provider.generate_image.return_value = {"status": "success", "filename": "test.png"}

        generate_single_image(
            mock_provider,
            "test prompt",
            str(tmp_path),
            "test.png",
            model="gpt-image-1.5",
        )

        # Verify model was passed to provider
        mock_provider.generate_image.assert_called_once()
        call_kwargs = mock_provider.generate_image.call_args[1]
        assert call_kwargs["model"] == "gpt-image-1.5"

    def test_generate_single_image_accepts_none_model(self, tmp_path):
        """Test that generate_single_image handles None model."""
        from imggen.generator import generate_single_image
        from unittest.mock import MagicMock

        mock_provider = MagicMock()
        mock_provider.generate_image.return_value = {"status": "success", "filename": "test.png"}

        generate_single_image(
            mock_provider,
            "test prompt",
            str(tmp_path),
            "test.png",
        )

        # Verify model was passed (as None)
        mock_provider.generate_image.assert_called_once()
        call_kwargs = mock_provider.generate_image.call_args[1]
        assert call_kwargs["model"] is None
