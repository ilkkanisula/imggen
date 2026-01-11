"""Image generation functionality for imggen."""

import os
import sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from imggen.pricing import calculate_image_cost
from imggen.providers import get_provider, infer_provider_from_model
from imggen.config import get_api_key_for_provider


def check_file_collisions(output_dir: str, variations: int) -> tuple[bool, list[str]]:
    """Check if files imggen_001.png through imggen_{variations}.png exist.

    Args:
        output_dir: Directory to check
        variations: Number of expected images

    Returns:
        (has_collision, list_of_existing_files)
    """
    collisions = []
    for i in range(1, variations + 1):
        filename = f"imggen_{i:03d}.png"
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            collisions.append(filename)
    return len(collisions) > 0, collisions


def format_collision_error(collisions: list[str], output_dir: str) -> str:
    """Format collision error message.

    Args:
        collisions: List of existing filenames
        output_dir: Output directory path

    Returns:
        Formatted error message
    """
    lines = ["Error: File collision detected", ""]
    lines.append(f"The following files already exist in {output_dir}:")
    for filename in collisions:
        lines.append(f"  - {filename}")
    lines.append("")
    lines.append("Please:")
    lines.append("  1. Delete or rename these files, OR")
    lines.append("  2. Use a different --output directory")
    lines.append("")
    lines.append("No API calls were made (no charges incurred).")
    return "\n".join(lines)


def generate_single_image(
    provider,
    prompt: str,
    output_dir: str,
    filename: str,
    aspect_ratio: str = None,
    resolution: str = None,
    quality: str = None,
    reference_images: list[str] = None,
    model: str = None,
    input_fidelity: str = None,
) -> dict:
    """Generate a single image and save it.

    Args:
        provider: Provider instance
        prompt: Image generation prompt
        output_dir: Output directory
        filename: Output filename (with .png extension)
        aspect_ratio: Optional aspect ratio (e.g., "16:9")
        resolution: Optional resolution for Google (e.g., "2K")
        quality: Optional quality for OpenAI (e.g., "medium")
        reference_images: Optional list of reference image paths
        model: Optional model name
        input_fidelity: Optional OpenAI input fidelity ("high"/"low")

    Returns:
        Dict with status and optional error
        - {"status": "success", "filename": str}
        - {"status": "failed", "error": str, "rate_limited": bool}
    """
    try:
        result = provider.generate_image(
            prompt,
            output_dir,
            filename,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            quality=quality,
            reference_images=reference_images,
            model=model,
            input_fidelity=input_fidelity,
        )
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def generate_from_prompt(
    prompt: str,
    reference_images: list[str],
    output_dir: str,
    variations: int,
    provider_name: str,
    api_key: str,
    aspect_ratio: str = None,
    quality: str = None,
    resolution: str = None,
    model: str = None,
    input_fidelity: str = None,
    dry_run: bool = False,
) -> None:
    """Generate images from prompt and save to disk.

    Args:
        prompt: Image generation prompt
        reference_images: List of reference image paths
        output_dir: Output directory
        variations: Number of variations to generate (1-4)
        provider_name: Provider name ("openai" or "google")
        api_key: API key for provider
        aspect_ratio: Optional aspect ratio
        quality: Optional quality (OpenAI)
        resolution: Optional resolution (Google)
        model: Optional model override
        input_fidelity: Optional OpenAI input fidelity ("high"/"low")
        dry_run: If True, show cost estimate and exit

    Raises:
        ValueError: If file collisions detected or other errors
    """
    # Normalize output directory path
    output_dir = output_dir.rstrip(os.sep)

    # Check file collisions BEFORE any API calls
    has_collision, collisions = check_file_collisions(output_dir, variations)
    if has_collision:
        raise ValueError(format_collision_error(collisions, output_dir))

    # Determine provider
    if model:
        provider_name = infer_provider_from_model(model)
        api_key = get_api_key_for_provider(provider_name)

    provider = get_provider(provider_name, api_key)

    # Calculate cost estimate
    cost_per_image = calculate_image_cost(provider_name, quality, resolution)
    estimated_cost = cost_per_image * variations

    # Display pre-generation info
    print(f"Generating {variations} image{'s' if variations > 1 else ''} with {provider_name.title()} ({provider.get_generate_model()})")
    print()
    print("Configuration:")
    print(f"  Prompt: \"{prompt}\"")
    if quality:
        print(f"  Quality: {quality}")
    if resolution:
        print(f"  Resolution: {resolution}")
    if aspect_ratio:
        print(f"  Aspect ratio: {aspect_ratio}")
    if input_fidelity:
        print(f"  Input fidelity: {input_fidelity}")
    if reference_images:
        print(f"  Reference images: {', '.join(reference_images)}")
    print(f"  Variations: {variations}")
    print(f"  Output: {output_dir}/imggen_001.png ... {output_dir}/imggen_{variations:03d}.png")
    print()
    print(f"Estimated cost: ${estimated_cost:.2f}")

    # If dry run, exit here
    if dry_run:
        print()
        print("Run without --dry-run to generate images.")
        return

    # Generate images in parallel
    print()
    successful = 0
    failed = 0
    errors = []
    rate_limited = False

    # Use up to 4 parallel workers
    max_workers = min(4, variations)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all generation tasks
        futures = {}
        for i in range(1, variations + 1):
            filename = f"imggen_{i:03d}.png"
            future = executor.submit(
                generate_single_image,
                provider,
                prompt,
                output_dir,
                filename,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                quality=quality,
                reference_images=reference_images,
                model=model,
                input_fidelity=input_fidelity,
            )
            futures[future] = (i, filename)

        # Collect results and display them in order
        results = {}
        for future in as_completed(futures):
            i, filename = futures[future]
            result = future.result()
            results[i] = (filename, result)

            if result.get("rate_limited"):
                rate_limited = True
                # Cancel remaining tasks
                executor.shutdown(wait=False)
                break

        # Display results in sequential order
        for i in range(1, variations + 1):
            if i in results:
                filename, result = results[i]
                if result["status"] == "success":
                    print(f"  [{i}/{variations}] Generating {filename}... ✓")
                    successful += 1
                else:
                    print(f"  [{i}/{variations}] Generating {filename}... ✗")
                    failed += 1
                    errors.append(f"  - {filename}: {result.get('error', 'Unknown error')}")

    # Calculate actual cost based on successful images
    actual_cost = cost_per_image * successful

    # Summary
    print()
    print("=" * 50)
    print("Generation complete!")
    print(f"  Successful: {successful}/{successful + failed}")
    if failed > 0:
        print(f"  Failed: {failed}/{successful + failed}")
        print()
        print("Errors:")
        for error in errors:
            print(error)
    print()
    print(f"Actual cost: ${actual_cost:.2f}")
    print(f"Output directory: {output_dir}")
