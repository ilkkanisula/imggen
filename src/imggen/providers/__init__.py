"""Provider abstraction for multi-provider image generation support."""

from abc import ABC, abstractmethod

# Available models per provider
AVAILABLE_MODELS = {
    "openai": ["gpt-image-1.5"],
    "google": ["gemini-3-pro-image-preview"],
}


class Provider(ABC):
    """Base provider interface for image generation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = ""  # "google" or "openai"

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        output_dir: str,
        filename: str,
        aspect_ratio: str = None,
        resolution: str = None,
        quality: str = None,
        reference_images: list = None,
        model: str = None,
        input_fidelity: str = None,
    ) -> dict:
        """Generate a single image and save to disk.

        Args:
            prompt: Image generation prompt
            output_dir: Directory to save image
            filename: Filename for the image (with .png extension)
            aspect_ratio: Optional aspect ratio (e.g., "16:9")
            resolution: Optional resolution for Google (e.g., "2K")
            quality: Optional quality for OpenAI (e.g., "medium")
            reference_images: Optional list of reference image paths
            model: Optional model name (uses provider default if not specified)
            input_fidelity: Optional OpenAI input fidelity for reference images ("high"/"low")

        Returns:
            Dict with status and optional error info
            - {"status": "success", "filename": str}
            - {"status": "failed", "error": str, "rate_limited": bool}
        """
        raise NotImplementedError

    @abstractmethod
    def get_generate_model(self) -> str:
        """Return default model name for generation."""
        raise NotImplementedError


def get_provider(provider_name: str, api_key: str) -> Provider:
    """Factory to create provider instance.

    Args:
        provider_name: "google" or "openai"
        api_key: API key for the provider

    Returns:
        Provider instance

    Raises:
        ValueError: If provider name is unknown
    """
    if provider_name == "google":
        from imggen.providers.google_provider import GoogleProvider
        return GoogleProvider(api_key)
    elif provider_name == "openai":
        from imggen.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(api_key)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def infer_provider_from_model(model_name: str) -> str:
    """Infer provider from model name.

    Args:
        model_name: Model identifier (e.g., "gpt-image-1.5", "gemini-3-pro-image-preview")

    Returns:
        Provider name: "google" or "openai"
    """
    if model_name.startswith("gemini-") or model_name.startswith("google-"):
        return "google"
    elif model_name.startswith("gpt-") or model_name.startswith("dall-e-"):
        return "openai"
    else:
        # Default to OpenAI
        return "openai"


def get_available_models() -> dict[str, list[str]]:
    """Get all available models grouped by provider.

    Returns:
        Dict mapping provider names to list of available models
    """
    return AVAILABLE_MODELS


def get_models_for_provider(provider_name: str) -> list[str]:
    """Get available models for a specific provider.

    Args:
        provider_name: Provider name ("google" or "openai")

    Returns:
        List of available models for the provider, empty list if provider unknown
    """
    return AVAILABLE_MODELS.get(provider_name, [])
