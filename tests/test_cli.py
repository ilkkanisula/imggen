"""Tests for CLI argument parsing and validation."""
import os
import pytest
from imggen.cli import load_prompt, load_references, validate_arguments


class TestPromptLoading:
    """Tests for load_prompt function."""

    def test_load_prompt_from_text(self):
        """Test loading prompt directly from text."""
        prompt = load_prompt(prompt_text="a beautiful landscape")
        assert prompt == "a beautiful landscape"

    def test_load_prompt_from_file(self, tmp_path):
        """Test loading prompt from file."""
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("serene mountain at sunset")

        prompt = load_prompt(prompt_file=str(prompt_file))
        assert prompt == "serene mountain at sunset"

    def test_load_prompt_from_file_with_whitespace(self, tmp_path):
        """Test loading prompt from file strips whitespace."""
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("  a beautiful landscape  \n")

        prompt = load_prompt(prompt_file=str(prompt_file))
        assert prompt == "a beautiful landscape"

    def test_load_prompt_file_not_found(self):
        """Test error when prompt file not found."""
        with pytest.raises(ValueError, match="Prompt file not found"):
            load_prompt(prompt_file="/nonexistent/file.txt")

    def test_load_prompt_file_empty(self, tmp_path):
        """Test error when prompt file is empty."""
        prompt_file = tmp_path / "empty.txt"
        prompt_file.write_text("")

        with pytest.raises(ValueError, match="Prompt file is empty"):
            load_prompt(prompt_file=str(prompt_file))

    def test_load_prompt_requires_input(self):
        """Test error when no prompt source provided."""
        with pytest.raises(ValueError, match="Must provide either --prompt or --file"):
            load_prompt()

    def test_load_prompt_prefers_text_over_file(self, tmp_path):
        """Test that text prompt takes precedence if both provided."""
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("file prompt")

        prompt = load_prompt(prompt_text="text prompt", prompt_file=str(prompt_file))
        assert prompt == "text prompt"


class TestReferenceLoading:
    """Tests for load_references function."""

    def test_load_references_empty(self):
        """Test loading when no references provided."""
        refs = load_references()
        assert refs == []

    def test_load_references_positional(self):
        """Test loading references from positional arguments."""
        refs = load_references(reference_paths=["ref1.jpg", "ref2.jpg"])
        assert refs == ["ref1.jpg", "ref2.jpg"]

    def test_load_references_from_file(self, tmp_path):
        """Test loading references from file."""
        refs_file = tmp_path / "refs.txt"
        refs_file.write_text("ref1.jpg\nref2.jpg\nref3.jpg")

        refs = load_references(reference_file=str(refs_file))
        assert refs == ["ref1.jpg", "ref2.jpg", "ref3.jpg"]

    def test_load_references_from_file_skips_empty_lines(self, tmp_path):
        """Test that empty lines are skipped."""
        refs_file = tmp_path / "refs.txt"
        refs_file.write_text("ref1.jpg\n\nref2.jpg\n  \nref3.jpg")

        refs = load_references(reference_file=str(refs_file))
        assert refs == ["ref1.jpg", "ref2.jpg", "ref3.jpg"]

    def test_load_references_file_not_found(self):
        """Test error when references file not found."""
        with pytest.raises(ValueError, match="References file not found"):
            load_references(reference_file="/nonexistent/refs.txt")

    def test_load_references_file_empty(self, tmp_path):
        """Test error when references file is empty."""
        refs_file = tmp_path / "empty.txt"
        refs_file.write_text("")

        with pytest.raises(ValueError, match="References file is empty"):
            load_references(reference_file=str(refs_file))

    def test_load_references_both_specified_error(self, tmp_path):
        """Test error when both positional and file references provided."""
        refs_file = tmp_path / "refs.txt"
        refs_file.write_text("ref1.jpg")

        with pytest.raises(ValueError, match="Cannot specify both positional reference images and --references file"):
            load_references(reference_paths=["ref1.jpg"], reference_file=str(refs_file))


class TestArgumentValidation:
    """Tests for validate_arguments function."""

    def test_validate_arguments_valid_minimal(self):
        """Test validation passes with minimal valid arguments."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test prompt"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_aspect_ratio_valid(self):
        """Test valid aspect ratios pass validation."""
        class Args:
            aspect_ratio = "16:9"
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_aspect_ratio_invalid(self):
        """Test invalid aspect ratio fails validation."""
        class Args:
            aspect_ratio = "invalid"
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Invalid aspect ratio"):
            validate_arguments(Args())

    def test_validate_quality_low(self):
        """Test low quality passes validation."""
        class Args:
            aspect_ratio = None
            quality = "low"
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_quality_medium(self):
        """Test medium quality passes validation."""
        class Args:
            aspect_ratio = None
            quality = "medium"
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_quality_high(self):
        """Test high quality passes validation."""
        class Args:
            aspect_ratio = None
            quality = "high"
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_quality_invalid(self):
        """Test invalid quality fails validation."""
        class Args:
            aspect_ratio = None
            quality = "ultra"
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Invalid quality level"):
            validate_arguments(Args())

    def test_validate_resolution_1k(self):
        """Test 1K resolution passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = "1K"
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_resolution_2k(self):
        """Test 2K resolution passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = "2K"
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_resolution_4k(self):
        """Test 4K resolution passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = "4K"
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_resolution_invalid(self):
        """Test invalid resolution fails validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = "8K"
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Invalid resolution"):
            validate_arguments(Args())

    def test_validate_variations_1(self):
        """Test 1 variation passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_variations_2(self):
        """Test 2 variations pass validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 2
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_variations_3(self):
        """Test 3 variations pass validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 3
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_variations_4(self):
        """Test 4 variations pass validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 4
            prompt = "test"
            file = None
            reference_images = []
            references = None

        validate_arguments(Args())  # Should not raise

    def test_validate_variations_too_low(self):
        """Test variations below 1 fails validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 0
            prompt = "test"
            file = None
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Variations must be between 1 and 4"):
            validate_arguments(Args())

    def test_validate_variations_too_high(self):
        """Test variations above 4 fails validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 5
            prompt = "test"
            file = None
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Variations must be between 1 and 4"):
            validate_arguments(Args())

    def test_validate_prompt_required(self):
        """Test that prompt or file is required."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = None
            file = None
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Must provide either --prompt or --file"):
            validate_arguments(Args())

    def test_validate_prompt_mutually_exclusive(self):
        """Test that prompt and file cannot both be specified."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = "test.txt"
            reference_images = []
            references = None

        with pytest.raises(ValueError, match="Cannot specify both --prompt and --file"):
            validate_arguments(Args())

    def test_validate_reference_images_mutually_exclusive(self):
        """Test that reference_images and references cannot both be specified."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = ["ref1.jpg"]
            references = "refs.txt"

        with pytest.raises(ValueError, match="Cannot specify both positional reference images and --references file"):
            validate_arguments(Args())

    def test_validate_input_fidelity_high(self):
        """Test input_fidelity='high' passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None
            input_fidelity = "high"

        validate_arguments(Args())  # Should not raise

    def test_validate_input_fidelity_low(self):
        """Test input_fidelity='low' passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None
            input_fidelity = "low"

        validate_arguments(Args())  # Should not raise

    def test_validate_input_fidelity_none(self):
        """Test input_fidelity=None passes validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None
            input_fidelity = None

        validate_arguments(Args())  # Should not raise

    def test_validate_input_fidelity_invalid(self):
        """Test invalid input_fidelity fails validation."""
        class Args:
            aspect_ratio = None
            quality = None
            resolution = None
            variations = 1
            prompt = "test"
            file = None
            reference_images = []
            references = None
            input_fidelity = "invalid"

        with pytest.raises(ValueError, match="Invalid input_fidelity"):
            validate_arguments(Args())


class TestListModelsCommand:
    """Tests for list-models command."""

    def test_list_models_command_outputs_models(self, capsys):
        """Test that list-models command outputs available models."""
        from imggen.cli import main
        import sys
        from unittest.mock import patch

        with patch.object(sys, "argv", ["imggen", "list-models"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Available image generation models:" in captured.out
            assert "gpt-image-1.5" in captured.out
            assert "gemini-3-pro-image-preview" in captured.out

    def test_list_models_shows_provider_names(self, capsys):
        """Test that list-models shows provider names."""
        from imggen.cli import main
        import sys
        from unittest.mock import patch

        with patch.object(sys, "argv", ["imggen", "list-models"]):
            with pytest.raises(SystemExit):
                main()

            captured = capsys.readouterr()
            assert "Openai:" in captured.out or "OpenAI:" in captured.out.replace("Openai", "OpenAI")
            assert "Google:" in captured.out
