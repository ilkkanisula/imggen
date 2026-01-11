"""Tests for pricing calculations."""
import pytest
from imggen.pricing import calculate_image_cost


class TestPricingCalculations:
    """Tests for cost calculations across providers and quality settings."""

    def test_calculate_image_cost_openai_default(self):
        """Test cost calculation for OpenAI default settings."""
        cost = calculate_image_cost("openai", None, None)
        assert cost == 0.009  # low quality default

    def test_calculate_image_cost_openai_low_quality(self):
        """Test cost calculation for OpenAI low quality."""
        cost = calculate_image_cost("openai", "low", None)
        assert cost == 0.009

    def test_calculate_image_cost_openai_medium_quality(self):
        """Test cost calculation for OpenAI medium quality."""
        cost = calculate_image_cost("openai", "medium", None)
        assert cost == 0.034

    def test_calculate_image_cost_openai_high_quality(self):
        """Test cost calculation for OpenAI high quality."""
        cost = calculate_image_cost("openai", "high", None)
        assert cost == 0.133

    def test_calculate_image_cost_google_default(self):
        """Test cost calculation for Google default settings."""
        cost = calculate_image_cost("google", None, "2K")
        assert cost == 0.134

    def test_calculate_image_cost_google_1k_resolution(self):
        """Test cost calculation for Google 1K resolution."""
        cost = calculate_image_cost("google", None, "1K")
        assert cost == 0.134

    def test_calculate_image_cost_google_2k_resolution(self):
        """Test cost calculation for Google 2K resolution."""
        cost = calculate_image_cost("google", None, "2K")
        assert cost == 0.134

    def test_calculate_image_cost_google_4k_resolution(self):
        """Test cost calculation for Google 4K resolution."""
        cost = calculate_image_cost("google", None, "4K")
        assert cost == 0.24

    def test_calculate_image_cost_google_quality_ignored(self):
        """Test that Google pricing ignores quality parameter."""
        cost_2k = calculate_image_cost("google", None, "2K")
        cost_2k_quality = calculate_image_cost("google", "high", "2K")
        assert cost_2k == cost_2k_quality == 0.134

    def test_calculate_image_cost_openai_resolution_ignored(self):
        """Test that OpenAI pricing ignores resolution parameter."""
        cost_low = calculate_image_cost("openai", "low", None)
        cost_low_res = calculate_image_cost("openai", "low", "4K")
        assert cost_low == cost_low_res == 0.009
