# OpenAI GPT Image 1.5 Reference Image Implementation Guide

**Date**: January 2026
**Research Summary**: OpenAI GPT Image 1.5 API capabilities for reference image support

## Executive Summary

**YES - GPT Image 1.5 SUPPORTS reference images** through the image-to-image transformation API. Unlike DALL-E 3 (which does NOT support reference images), GPT Image 1.5 enables:

- Providing one or more reference images as input
- High fidelity mode to preserve details from reference images
- Style transfer and composition guidance
- Image editing with targeted modifications

## Key Findings for Implementation

### 1. Reference Image Support - YES, Fully Supported

**What GPT Image 1.5 Enables:**
- Accept reference images as input to guide generation
- Multiple input images can be provided simultaneously
- Use input images for style transfer, composition, or direct editing

**What GPT Image 1.5 Does NOT Support:**
- DALL-E 3 does NOT support reference images at all (text-only)
- True pixel-level masking (uses "soft masking" instead - regenerates entire image)
- Inpainting with perfect unmasked region preservation

### 2. Technical Specifications for Reference Images

#### Image Input Format
- **Supported Formats**: PNG, JPEG, WebP
- **Maximum File Size**: < 50MB per image
- **Encoding Methods**:
  - Base64-encoded data URLs embedded in request
  - File IDs created through OpenAI Files API
  - OpenAI working to support direct URLs (coming soon)

#### Image Input Processing
- Images are converted to tokens and charged separately
- 1024×1024 image in high detail mode = 765 tokens
- Token cost depends on image dimensions (larger images = more tokens)
- Images are scaled to fit 2048×2048 bounding box, then tiled for token calculation

### 3. High Input Fidelity Mode - Critical for Reference Images

**What High Input Fidelity Does:**
```
When input_fidelity = "high":
- Model preserves details from input images with remarkable precision
- Maintains facial features, lighting, composition, spatial relationships
- Applies only the textual modifications requested by user
- Significantly advances ability to preserve critical image elements
```

**Priority Order for Multiple Images:**
- First image receives priority for preservation with richer textures and finer details
- Additional images used for reference, styling, or supplementary elements

**Practical Example:**
```
Use Case: E-commerce product variation
- Primary image (first): Product photograph (will preserve shape, proportions, details)
- Secondary images: Sketches or mood boards (used for styling guidance)
- Result: Product variations with same exact product, different colors/poses/backgrounds
```

### 4. Image-to-Image Transformation Capabilities

#### Style Transfer
- Analyze uploaded image and extract visual characteristics
- Apply those characteristics to new subjects or scenes
- Consistency across multiple iterations when given stable reference

**What It Works Well For:**
- Applying artistic styles (painting, watercolor, photography styles)
- Transferring color palettes and lighting
- Maintaining visual coherence across multiple images

**Limitations:**
- Cannot use living artists' styles (copyright policy)
- Specific/niche aesthetic approaches sometimes less consistent
- Some artistic styles show regression vs. GPT Image 1

#### Image Editing
- Modify existing images using text prompts
- Preserve elements like lighting, composition, facial likeness
- Maintain consistency across successive edits

### 5. Inpainting Approach - Important Architectural Difference

**GPT Image 1.5 Uses "Soft Masking" NOT pixel-level masking:**

```
Traditional Inpainting (DALL-E 2):
- Masked areas: Precisely regenerated
- Unmasked areas: Preserved exactly as provided

GPT Image 1.5 Soft Masking:
- Regenerates ENTIRE image
- Unmasked regions weighted more heavily toward preservation
- Masked regions treated as guidelines, not hard constraints
```

**Practical Implication:**
- Do NOT expect pixel-perfect preservation of unmasked regions
- Small regeneration of entire image occurs
- Better for content-aware editing than precise spatial control

### 6. Limitations for Reference Image Implementation

**Technical Limitations:**
- Cannot guarantee pixel-perfect character consistency across multiple images
- Anatomical accuracy issues with hands and fingers
- Multiple faces in same image sometimes produce inconsistent quality
- Character rendering in different scenes has variations

**Style Limitations:**
- Living artist styles are restricted (copyright policy)
- Certain specific artistic styles show regression vs. earlier versions
- Multilingual text rendering challenges (Chinese, Arabic, Hebrew)
- Complex optical effects (transparency, reflections) sometimes unrealistic

**Content Policy Boundaries:**
- Political content prohibited
- Graphic violent content prohibited
- Adult content prohibited
- Copyrighted characters prohibited

### 7. Performance Characteristics

**Speed:**
- 4x faster than GPT Image 1
- Speed improvements for reference image processing vary by prompt complexity
- Streaming partial images available for progressive feedback

**Cost:**
- 20% reduction in token costs vs. GPT Image 1
- Image input costs: Based on dimensions, not flat rate
- Output always Base64-encoded (not URL-based like DALL-E 3)

**Quality Tiers:**
- Low quality: Fastest, cheapest (~$0.01)
- Medium quality: Balanced (~$0.04)
- High quality: Maximum fidelity (~$0.17)

### 8. API Parameters for Reference Image Implementation

```python
# Key parameters for reference image support
{
    "model": "gpt-image-1.5",
    "prompt": "description of desired modifications",
    "image": <base64_encoded_image>,  # Primary reference image
    "input_fidelity": "high",          # Preserve reference details
    "quality": "high",                 # low, medium, high
    "size": "1024x1024",              # 1024x1024, 1536x1024, 1024x1536
    "n": 1,                           # Number of images to generate
    "temperature": 0.0,               # Consistency of reference preservation
}

# Multiple images (if supported):
# Submit first image as primary (gets priority preservation)
# Additional images handled separately or in sequence
```

## Recommendations for imggen Implementation

### What We CAN Implement Now:
1. ✅ Accept reference images via CLI (`positional args` or `-r file`)
2. ✅ Upload reference images to OpenAI API
3. ✅ Use Base64 encoding for image data
4. ✅ Set `input_fidelity="high"` for reference preservation
5. ✅ Support style transfer use cases
6. ✅ Support product/character variation generation

### What We SHOULD NOT Expect:
1. ❌ Pixel-perfect character consistency (inherent limitation)
2. ❌ True inpainting with pixel-level masking (soft masking only)
3. ❌ Living artist style references (policy restriction)
4. ❌ Perfect anatomical accuracy (known limitation)

### What NEEDS Research/Testing:
1. Google Gemini's reference image support (if planning Google provider support)
2. Exact API endpoint for multiple reference images
3. Performance impact of Base64 encoding large images
4. Optimal prompt phrasing for style transfer vs. composition guidance

## Related Features Not Yet Supported in imggen:

- **Outpainting**: Extending images beyond original boundaries
- **Inpainting with masks**: Selective region regeneration
- **Multiple input images**: Using 2+ reference images simultaneously
- **Streaming partial images**: Progressive generation feedback

## Future Implementation Phases:

**Phase 1 (Current):** Document and research ✅
**Phase 2:** Implement basic reference image support
- Accept reference images from CLI
- Base64 encode and pass to OpenAI API
- Set input_fidelity="high" for preservation

**Phase 3:** Advanced features
- Multiple reference image support
- Inpainting with mask support
- Streaming partial images for UX feedback

**Phase 4:** Google provider support
- Research Gemini reference image capabilities
- Implement if supported

## References & Resources

- OpenAI Image Generation API Docs: https://platform.openai.com/docs/guides/image-generation
- GPT Image 1.5 Model Card: https://platform.openai.com/docs/models/gpt-image-1.5
- Research Source: Comprehensive 2026 research summary on OpenAI image generation capabilities

## Implementation Status for imggen

### ✅ SOLUTION FOUND: Use `client.images.edit()` API

**The Issue**: `client.images.generate()` is text-to-image ONLY
**The Solution**: Use `client.images.edit()` for image-to-image with reference images

### Correct API Endpoints (from Official OpenAI Docs - 2026)

The Image API provides **THREE endpoints**:

1. **Generations** (`client.images.generate()`)
   - Generate images from scratch
   - Text prompt only - NO reference image support
   - This is what we were using

2. **Edits** (`client.images.edit()`) ✅ **THIS IS WHAT WE NEED**
   - Modify existing images using a new prompt
   - **Supports reference images**
   - Parameters: `image`, `prompt`, `mask` (optional)

3. **Variations** (`client.images.create_variation()`)
   - Generate variations of an existing image
   - DALL-E 2 only, not available for GPT Image

### Working Implementation (Python)

```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

# Edit/modify an existing image with reference
response = client.images.edit(
    model="gpt-image-1",  # or gpt-image-1.5
    image=open("reference.jpg", "rb"),  # Reference image
    prompt="apply style: studio ghibli, warm colors",
    n=1,
    quality="high",
    size="1024x1024",
)

# Save result
image_base64 = response.data[0].b64_json
with open("output.png", "wb") as f:
    f.write(base64.b64decode(image_base64))
```

### Key Parameters for `client.images.edit()`

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `model` | str | Yes | `gpt-image-1` or `gpt-image-1.5` |
| `image` | file | Yes | Reference image file object |
| `prompt` | str | Yes | Text description of desired edits |
| `mask` | file | No | Mask for inpainting (optional) |
| `n` | int | No | Number of variations (1-10) |
| `size` | str | No | `1024x1024`, `1536x1024`, `1024x1536` |
| `quality` | str | No | `low`, `medium`, `high`, `auto` |

### Implementation Path for imggen

To implement reference image support in imggen:

**Phase 1** (Simple): Use `client.images.edit()` instead of `client.images.generate()`
```python
# In OpenAI provider
if reference_images and len(reference_images) > 0:
    response = self.client.images.edit(
        model=GENERATE_MODEL,
        image=open(reference_images[0], "rb"),
        prompt=full_prompt,
        n=1,
        quality=openai_quality,
        size=image_size,
    )
else:
    # Fall back to generation-only
    response = self.client.images.generate(
        model=GENERATE_MODEL,
        prompt=full_prompt,
        n=1,
        quality=openai_quality,
        size=image_size,
    )
```

**Phase 2** (Advanced): Support masking for inpainting

### Alternative: Responses API

OpenAI also supports image generation via `client.responses.create()` with image-to-image capabilities:
```python
response = client.responses.create(
    model="gpt-image-1.5",
    input="Generate image based on reference",
    tools=[{"type": "image_generation"}],
    # Can include image reference here
)
```

### Summary

✅ **Reference images ARE supported in OpenAI API**
✅ **The correct method is `client.images.edit()`**
✅ **Works with GPT Image 1 and GPT Image 1.5**
✅ **Python SDK fully supports it** (as of April 2025+)

The reason we got an error is we tried to add `image` parameter to `images.generate()` - that's the wrong endpoint. We need to switch to `images.edit()` instead.
