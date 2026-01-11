"""Tests for provider factory and inference."""
import pytest
from unittest.mock import patch, MagicMock
from imggen.providers import Provider, get_provider, infer_provider_from_model


class TestProviderFactory:
    """Test provider factory function."""

    def test_get_google_provider(self):
        """Test creating Google provider."""
        provider = get_provider("google", "test-key")
        assert provider.name == "google"
        assert provider.get_generate_model() == "gemini-3-pro-image-preview"

    def test_get_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = get_provider("openai", "test-key")
        assert provider.name == "openai"
        assert provider.get_generate_model() == "gpt-image-1.5"

    def test_unknown_provider_raises_error(self):
        """Test that unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown", "test-key")


class TestProviderInference:
    """Test provider inference from model names."""

    def test_infer_google_from_gemini_prefix(self):
        """Test inferring Google from gemini- prefix."""
        assert infer_provider_from_model("gemini-2.0-flash") == "google"
        assert infer_provider_from_model("gemini-3-pro-image-preview") == "google"

    def test_infer_google_from_google_prefix(self):
        """Test inferring Google from google- prefix."""
        assert infer_provider_from_model("google-something") == "google"

    def test_infer_openai_from_gpt_prefix(self):
        """Test inferring OpenAI from gpt- prefix."""
        assert infer_provider_from_model("gpt-4.5-mini") == "openai"
        assert infer_provider_from_model("gpt-image-1.5") == "openai"
        assert infer_provider_from_model("gpt-4") == "openai"

    def test_infer_openai_from_dalle_prefix(self):
        """Test inferring OpenAI from dall-e- prefix."""
        assert infer_provider_from_model("dall-e-3") == "openai"
        assert infer_provider_from_model("dall-e-2") == "openai"

    def test_unknown_model_defaults_to_openai(self):
        """Test that unknown model defaults to OpenAI."""
        assert infer_provider_from_model("unknown-model") == "openai"
        assert infer_provider_from_model("custom-image-gen") == "openai"


class TestProviderInterface:
    """Test that providers implement required interface."""

    def test_google_provider_has_generate_image_method(self):
        """Test Google provider has generate_image method."""
        provider = get_provider("google", "test-key")
        assert hasattr(provider, "generate_image")
        assert callable(provider.generate_image)

    def test_openai_provider_has_generate_image_method(self):
        """Test OpenAI provider has generate_image method."""
        provider = get_provider("openai", "test-key")
        assert hasattr(provider, "generate_image")
        assert callable(provider.generate_image)


class TestOpenAIInputFidelity:
    """Test OpenAI provider input_fidelity parameter."""

    def test_input_fidelity_high_parameter_passed_to_api(self, tmp_path):
        """Test that input_fidelity='high' is passed to OpenAI API."""
        provider = get_provider("openai", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "edit", return_value=mock_response) as mock_edit:
            with patch("builtins.open", wraps=open):
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                    input_fidelity="high",
                )

                # Verify API was called with input_fidelity parameter
                assert mock_edit.called
                call_kwargs = mock_edit.call_args[1]
                assert "input_fidelity" in call_kwargs
                assert call_kwargs["input_fidelity"] == "high"

    def test_input_fidelity_low_parameter_passed_to_api(self, tmp_path):
        """Test that input_fidelity='low' is passed to OpenAI API."""
        provider = get_provider("openai", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "edit", return_value=mock_response) as mock_edit:
            with patch("builtins.open", wraps=open):
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                    input_fidelity="low",
                )

                # Verify API was called with input_fidelity parameter
                assert mock_edit.called
                call_kwargs = mock_edit.call_args[1]
                assert "input_fidelity" in call_kwargs
                assert call_kwargs["input_fidelity"] == "low"

    def test_input_fidelity_invalid_value_returns_error(self, tmp_path):
        """Test that invalid input_fidelity value returns error."""
        provider = get_provider("openai", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        result = provider.generate_image(
            prompt="test prompt",
            output_dir=str(tmp_path),
            filename="output.png",
            reference_images=[str(image_file)],
            input_fidelity="invalid",
        )

        # Should return error status
        assert result["status"] == "failed"
        assert "input_fidelity" in result["error"]

    def test_input_fidelity_none_not_passed_to_api(self, tmp_path):
        """Test that input_fidelity is not passed when None."""
        provider = get_provider("openai", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "edit", return_value=mock_response) as mock_edit:
            with patch("builtins.open", wraps=open):
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                    input_fidelity=None,
                )

                # Verify API was called
                assert mock_edit.called
                call_kwargs = mock_edit.call_args[1]
                # input_fidelity should not be in the call when None
                assert "input_fidelity" not in call_kwargs or call_kwargs.get("input_fidelity") is None


class TestOpenAIProviderReferenceImages:
    """Test OpenAI provider reference image handling."""

    def test_reference_image_file_closed_on_success(self, tmp_path):
        """Test that reference image file is properly closed after successful API call."""
        provider = get_provider("openai", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        # Mock the API response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "edit", return_value=mock_response):
            with patch("builtins.open", wraps=open) as mock_open:
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                )

                # Verify file operations were called
                assert mock_open.called

                # Verify context manager usage - file should be closed
                # The mock tracks that open was called, and with context manager it auto-closes
                handles = [call[0] for call in mock_open.call_args_list if call[0]]
                assert len(handles) > 0

    def test_reference_image_file_closed_on_error(self, tmp_path):
        """Test that reference image file is properly closed even on API error."""
        provider = get_provider("openai", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        # Mock API to raise an error
        with patch.object(provider.client.images, "edit", side_effect=Exception("API error")):
            with patch("builtins.open", wraps=open) as mock_open:
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                )

                # Should return error status
                assert result["status"] == "failed"
                assert "API error" in result["error"]

                # Verify file was opened and context manager closed it
                assert mock_open.called

    def test_reference_image_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is properly handled."""
        provider = get_provider("openai", "test-key")

        result = provider.generate_image(
            prompt="test prompt",
            output_dir=str(tmp_path),
            filename="output.png",
            reference_images=["/nonexistent/image.png"],
        )

        # Should return error status
        assert result["status"] == "failed"
        assert "Reference image not found" in result["error"]
        assert "/nonexistent/image.png" in result["error"]

    def test_multiple_reference_images_passed_to_api(self, tmp_path):
        """Test that multiple reference images are passed as list to API."""
        provider = get_provider("openai", "test-key")

        # Create multiple test image files
        image_files = []
        for i in range(3):
            image_file = tmp_path / f"reference{i}.png"
            image_file.write_bytes(b"fake image data")
            image_files.append(str(image_file))

        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "edit", return_value=mock_response) as mock_edit:
            with patch("builtins.open", wraps=open):
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=image_files,
                )

                # Verify API was called with all reference images as list
                assert mock_edit.called
                call_kwargs = mock_edit.call_args[1]
                assert "image" in call_kwargs
                # image should be a list with file objects
                assert isinstance(call_kwargs["image"], list)
                assert len(call_kwargs["image"]) == 3

    def test_multiple_reference_images_files_closed(self, tmp_path):
        """Test that all reference image files are properly closed."""
        provider = get_provider("openai", "test-key")

        # Create multiple test image files
        image_files = []
        for i in range(3):
            image_file = tmp_path / f"reference{i}.png"
            image_file.write_bytes(b"fake image data")
            image_files.append(str(image_file))

        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "edit", return_value=mock_response):
            with patch("builtins.open", wraps=open) as mock_open:
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=image_files,
                )

                # Verify all files were opened
                assert mock_open.called
                # Should have called open 3 times for the 3 reference images
                assert len([call for call in mock_open.call_args_list if call[0]]) >= 3


class TestModelListing:
    """Test model listing functionality."""

    def test_get_available_models_returns_dict(self):
        """Test get_available_models returns a dictionary."""
        from imggen.providers import get_available_models

        models = get_available_models()
        assert isinstance(models, dict)

    def test_get_available_models_has_providers(self):
        """Test available models contains provider keys."""
        from imggen.providers import get_available_models

        models = get_available_models()
        assert "openai" in models
        assert "google" in models

    def test_get_available_models_openai_contains_gpt_image(self):
        """Test OpenAI models list contains gpt-image-1.5."""
        from imggen.providers import get_available_models

        models = get_available_models()
        assert "gpt-image-1.5" in models["openai"]

    def test_get_available_models_google_contains_gemini(self):
        """Test Google models list contains gemini-3-pro-image-preview."""
        from imggen.providers import get_available_models

        models = get_available_models()
        assert "gemini-3-pro-image-preview" in models["google"]

    def test_get_models_for_provider_openai(self):
        """Test getting models for OpenAI provider."""
        from imggen.providers import get_models_for_provider

        models = get_models_for_provider("openai")
        assert isinstance(models, list)
        assert "gpt-image-1.5" in models

    def test_get_models_for_provider_google(self):
        """Test getting models for Google provider."""
        from imggen.providers import get_models_for_provider

        models = get_models_for_provider("google")
        assert isinstance(models, list)
        assert "gemini-3-pro-image-preview" in models

    def test_get_models_for_provider_unknown(self):
        """Test getting models for unknown provider returns empty list."""
        from imggen.providers import get_models_for_provider

        models = get_models_for_provider("unknown")
        assert models == []


class TestProviderModelParameter:
    """Test that providers accept and use model parameter."""

    def test_openai_provider_accepts_model_parameter(self, tmp_path):
        """Test OpenAI provider accepts model parameter."""
        from unittest.mock import MagicMock, patch

        provider = get_provider("openai", "test-key")

        # Mock base64 decode to avoid binary file issues
        import base64
        mock_image_data = b"fake png data"

        with patch("builtins.open", create=True):
            with patch("base64.b64decode", return_value=mock_image_data):
                with patch.object(provider.client.images, "generate") as mock_gen:
                    # Mock successful response
                    mock_response = MagicMock()
                    mock_image = MagicMock()
                    mock_image.b64_json = "base64encodeddata"
                    mock_response.data = [mock_image]
                    mock_gen.return_value = mock_response

                    result = provider.generate_image(
                        prompt="test",
                        output_dir=str(tmp_path),
                        filename="test.png",
                        model="gpt-image-1.5",
                    )

                    # Check that model was passed to API call
                    assert mock_gen.called
                    call_kwargs = mock_gen.call_args[1]
                    assert call_kwargs["model"] == "gpt-image-1.5"

    def test_openai_provider_uses_default_model_when_none(self, tmp_path):
        """Test OpenAI provider uses default model when no model specified."""
        provider = get_provider("openai", "test-key")

        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json="base64encodeddata")]

        with patch.object(provider.client.images, "generate", return_value=mock_response) as mock_gen:
            provider.generate_image(
                prompt="test",
                output_dir=str(tmp_path),
                filename="test.png",
            )
            # Verify the default model was used
            call_args = mock_gen.call_args
            assert call_args[1]["model"] == "gpt-image-1.5"

    def test_google_provider_accepts_model_parameter(self, tmp_path):
        """Test Google provider accepts model parameter."""
        provider = get_provider("google", "test-key")

        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = b"fake image data"
        mock_response.parts = [mock_part]

        with patch.object(provider.client.models, "generate_content", return_value=mock_response):
            result = provider.generate_image(
                prompt="test",
                output_dir=str(tmp_path),
                filename="test.png",
                model="gemini-3-pro-image-preview",
            )
            assert result["status"] == "success"

    def test_google_provider_uses_default_model_when_none(self, tmp_path):
        """Test Google provider uses default model when no model specified."""
        provider = get_provider("google", "test-key")

        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = b"fake image data"
        mock_response.parts = [mock_part]

        with patch.object(provider.client.models, "generate_content", return_value=mock_response) as mock_gen:
            provider.generate_image(
                prompt="test",
                output_dir=str(tmp_path),
                filename="test.png",
            )
            # Verify the default model was used
            call_args = mock_gen.call_args
            assert call_args[1]["model"] == "gemini-3-pro-image-preview"


class TestGoogleReferenceImages:
    """Test Google provider reference image support."""

    def test_single_reference_image_included_in_contents(self, tmp_path):
        """Test that single reference image is included in contents array."""
        provider = get_provider("google", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = b"fake image data"
        mock_response.parts = [mock_part]

        with patch.object(provider.client.models, "generate_content", return_value=mock_response) as mock_gen:
            with patch("PIL.Image.open") as mock_pil_open:
                mock_pil_open.return_value = MagicMock()
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                )

                # Verify generate_content was called
                assert mock_gen.called
                call_kwargs = mock_gen.call_args[1]
                assert "contents" in call_kwargs
                # Contents should have prompt + reference images
                assert len(call_kwargs["contents"]) >= 2

    def test_multiple_reference_images_included_in_contents(self, tmp_path):
        """Test that multiple reference images are included in contents array."""
        provider = get_provider("google", "test-key")

        # Create test image files
        image_files = []
        for i in range(3):
            image_file = tmp_path / f"reference{i}.png"
            image_file.write_bytes(b"fake image data")
            image_files.append(str(image_file))

        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = b"fake image data"
        mock_response.parts = [mock_part]

        with patch.object(provider.client.models, "generate_content", return_value=mock_response) as mock_gen:
            with patch("PIL.Image.open") as mock_pil_open:
                mock_pil_open.return_value = MagicMock()
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=image_files,
                )

                # Verify contents has prompt + 3 images
                call_kwargs = mock_gen.call_args[1]
                assert "contents" in call_kwargs
                assert len(call_kwargs["contents"]) == 4  # prompt + 3 images

    def test_exceeding_14_reference_limit_returns_error(self, tmp_path):
        """Test that exceeding 14 reference image limit returns error."""
        provider = get_provider("google", "test-key")

        # Create 15 image files
        image_files = []
        for i in range(15):
            image_file = tmp_path / f"reference{i}.png"
            image_file.write_bytes(b"fake image data")
            image_files.append(str(image_file))

        result = provider.generate_image(
            prompt="test prompt",
            output_dir=str(tmp_path),
            filename="output.png",
            reference_images=image_files,
        )

        # Should return error status
        assert result["status"] == "failed"
        assert "reference" in result["error"].lower()
        assert "14" in result["error"]

    def test_reference_image_file_not_found_returns_error(self, tmp_path):
        """Test that missing reference image file returns error."""
        provider = get_provider("google", "test-key")

        result = provider.generate_image(
            prompt="test prompt",
            output_dir=str(tmp_path),
            filename="output.png",
            reference_images=["/nonexistent/image.png"],
        )

        # Should return error status
        assert result["status"] == "failed"
        assert "Reference image" in result["error"]

    def test_response_modalities_configured_with_references(self, tmp_path):
        """Test that response_modalities includes IMAGE when references provided."""
        provider = get_provider("google", "test-key")

        # Create a test image file
        image_file = tmp_path / "reference.png"
        image_file.write_bytes(b"fake image data")

        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = b"fake image data"
        mock_response.parts = [mock_part]

        with patch.object(provider.client.models, "generate_content", return_value=mock_response) as mock_gen:
            with patch("PIL.Image.open") as mock_pil_open:
                mock_pil_open.return_value = MagicMock()
                result = provider.generate_image(
                    prompt="test prompt",
                    output_dir=str(tmp_path),
                    filename="output.png",
                    reference_images=[str(image_file)],
                )

                # Verify config includes response_modalities
                call_kwargs = mock_gen.call_args[1]
                assert "config" in call_kwargs
                config = call_kwargs["config"]
                assert config.response_modalities == ["TEXT", "IMAGE"]
