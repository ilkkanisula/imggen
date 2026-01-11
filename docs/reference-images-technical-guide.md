# Reference Images Technical Guide

## Overview

Both OpenAI and Google providers support reference images to guide image generation, but with different capabilities, constraints, and optimal use cases.

## OpenAI GPT Image 1.5

### Capabilities
- Uses `images.edit()` endpoint (not `generate()`)
- Supports multiple reference images per request
- Supports `input_fidelity` parameter to control facial detail preservation

### Key Parameters

**input_fidelity** - Controls how strictly facial features are preserved:
- `"high"`: Preserves facial identity details, expressions, and features
- `"low"`: Allows reinterpretation of facial features while maintaining general pose/composition
- Default: API defaults to `"high"` when reference images are provided

**quality** - Image quality level:
- `"standard"`: Faster, lower cost
- `"hd"`: Higher quality, higher cost

**size** - Output image dimensions:
- `1024x1024` (default)
- `1024x1792`
- `1792x1024`

### API Behavior

The OpenAI edit endpoint processes requests with the following structure:
1. Accept a reference image (mask not supported in current implementation)
2. Apply the prompt modifications to the reference
3. Preserve aspects according to `input_fidelity` setting
4. Return a single generated image

### Best Practices

**For pose control with identity preservation:**
- Use `input_fidelity="high"`
- Include explicit constraints in prompt: "Preserve facial features and identity"
- Describe pose changes precisely
- Example prompt: "Change pose to sitting position, preserve facial features and identity"

**For style transfer:**
- Use `input_fidelity="low"` to allow artistic reinterpretation
- Describe desired style changes in prompt
- Reference describes base appearance, prompt describes modifications

**For background/environment changes:**
- Use `input_fidelity="high"` to keep subject identity consistent
- Clearly describe what should change vs. what should remain

### Limitations

- Only one reference image per request (API constraint)
- Pose changes can alter facial identity even with `input_fidelity="high"` (model limitation)
- Mask support not implemented in current imggen version
- Cannot preserve exact pixel-perfect details, only approximate features

## Google Gemini 3 Pro

### Capabilities
- Supports up to 14 reference images total
- Maximum composition: 5 humans + 6 objects (or other combinations within 14 total)
- Reference images embedded in `contents` array alongside prompt
- No explicit `input_fidelity` parameter (provided for interface compatibility but unused)
- Better results with explicit text descriptions than visual pose reference alone

### API Behavior

Reference images are integrated into the generation process:
1. Build `contents` array: `[prompt_text, Image, Image, ...]`
2. Each image after the prompt text is treated as a reference
3. Model interprets images in context of prompt descriptions
4. Requires `response_modalities=['TEXT', 'IMAGE']` for image output

### Role Assignment Pattern

Google works best with explicit role assignment in the prompt:
```
Person 1 (first image): [description and position]
Person 2 (second image): [description and position]
Object 1 (third image): [description and context]
```

This explicit indexing helps the model correctly map multiple references to their intended roles in the final composition.

### Best Practices

**For multi-person compositions:**
- Use explicit role assignment: "Person 1 (first image): ...", "Person 2 (second image): ..."
- Describe spatial relationships and interactions
- Provide context for the scene
- Example: "Person 1 (first image): standing on left. Person 2 (second image): sitting on right. Both in modern office setting."

**For group poses with interactions:**
- Number references explicitly
- Describe position and action for each person
- Include overall scene context
- Works well with up to 5 humans

**For product/style variations:**
- First image as base product
- Additional images as reference styles or variations
- Prompt describes how to combine them

**For complex compositions:**
- Multiple human figures (up to 5)
- Multiple objects/environments (up to 6)
- Maintain clear role assignment in prompt

### Limitations

- Text descriptions more reliable than visual pose inference (model doesn't guarantee pose matching)
- 14 image maximum (composition constraint)
- 5 human + 6 object breakdown suggests model architecture preferences
- Requires explicit indexing for disambiguation

## Comparison Matrix

| Feature | OpenAI GPT-1.5 | Google Gemini-3 Pro |
|---------|----------------|--------------------|
| Reference images | Multiple (unlimited) | Up to 14 |
| Human figures | Multiple | Up to 5 |
| Objects/styles | Multiple | Up to 6 |
| input_fidelity parameter | Yes ("high"/"low") | No (interface only) |
| Endpoint type | images.edit() | models.generate_content() |
| Pose precision | Good (fidelity-controlled) | Moderate (text-dependent) |
| Identity preservation | High (with input_fidelity) | Moderate |
| Multi-person scenes | Good | Excellent |
| Scene compositing | Excellent (multiple refs) | Good |
| Interface consistency | Yes | Yes (for compatibility) |

## When to Use Each Provider

**Choose OpenAI when:**
- Preserving facial identity is critical (use `input_fidelity="high"`)
- Multiple reference images for style, composition, or multi-scene blending
- Subject identity/pose control with reference images
- Quality and detail are prioritized
- Cost is less critical

**Choose Google when:**
- Multi-person group compositions (explicit indexing makes sense)
- Complex 5+ person scenes with spatial relationships
- Combining many object/environment references
- Explicit role assignment workflow preferred

## Implementation Notes

Both providers implement the same interface (`generate_image()` method with `input_fidelity` parameter) for consistency, even though Google doesn't use `input_fidelity`. This allows CLI and generator to pass the parameter uniformly without provider-specific branching.
