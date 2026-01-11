#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-genai",
#   "python-dotenv",
#   "pillow",
#   "pyyaml",
# ]
# ///
import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timezone
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not set in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# Constants
MAX_VARIATIONS = 4
ASPECT_RATIO_WHITELIST = ["1:1", "16:9", "9:16", "4:3", "3:4"]
RESOLUTION_WHITELIST = ["1K", "2K", "4K"]
PARSE_MODEL = "gemini-2.0-flash"
GENERATE_MODEL = "gemini-3-pro-image-preview"


def get_output_folder_name(input_file):
    """Generate output folder name from input file."""
    basename = os.path.splitext(os.path.basename(input_file))[0]
    return f"{basename}_output"

# JSON Schema for structured output parsing
BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "prompt": {"type": "string"},
                    "variations": {"type": "integer"},
                    "aspect_ratio": {"type": "string"},
                    "resolution": {"type": "string"},
                },
                "required": ["prompt", "variations"],
            },
        },
        "global_style_references": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["images"],
}


def generate_image_slug(prompt, index):
    """Generate a filesystem-safe slug from a prompt.

    Extracts 2-3 meaningful words from the prompt and converts to snake_case.
    Prioritizes distinctive words like gender, style, subjects.
    Falls back to 'image_{index}' if extraction fails.
    """
    import re

    # Common words to skip
    stop_words = {"a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "be", "no", "not", "that", "this"}

    # High-priority distinguishing words (if present, include them)
    priority_words = {"female", "male", "woman", "man", "girl", "boy", "women", "men", "dark", "light", "bright", "digital", "oil", "watercolor"}

    # Extract words (alphanumeric + underscores)
    words = re.findall(r'\b[a-z]+\b', prompt.lower())

    # Find priority words
    priority_found = [w for w in words if w in priority_words]

    # Filter out stop words and get meaningful words (exclude those already in priority)
    meaningful = [w for w in words if w not in stop_words and len(w) > 2 and w not in priority_words]

    if priority_found:
        # Start with priority words, then add other meaningful words
        slug_words = priority_found[:2] + meaningful[:1]
        slug = "_".join(slug_words)
    elif meaningful:
        # Take first 2-3 meaningful words
        slug_words = meaningful[:3]
        slug = "_".join(slug_words)
    else:
        # Fallback: use image_{index}
        slug = f"image_{index:03d}"
        return slug

    # Limit to 30 characters
    slug = slug[:30]

    # Ensure it's filesystem-safe (remove any remaining special chars)
    slug = re.sub(r'[^a-z0-9_]', '', slug)

    return slug


def validate_yaml(data):
    """Validate YAML structure and enforce constraints."""
    if not isinstance(data, dict) or "images" not in data:
        raise ValueError("YAML must contain 'images' key with list of image configs")

    if not isinstance(data["images"], list):
        raise ValueError("'images' must be a list")

    # Track used names to handle duplicates
    used_names = {}

    for i, image in enumerate(data["images"]):
        if not isinstance(image, dict):
            raise ValueError(f"Image {i} must be a dictionary")

        if "prompt" not in image or not image["prompt"]:
            raise ValueError(f"Image {i} must have a non-empty 'prompt'")

        # Set defaults and validate variations
        if "variations" not in image:
            image["variations"] = 4
        elif not isinstance(image["variations"], int) or image["variations"] < 1:
            raise ValueError(f"Image {i} variations must be a positive integer")

        if image["variations"] > MAX_VARIATIONS:
            image["variations"] = MAX_VARIATIONS

        # Generate or validate name field
        if "name" not in image:
            base_name = generate_image_slug(image["prompt"], i + 1)
        else:
            # Sanitize user-provided name
            import re
            base_name = re.sub(r'[^a-z0-9_-]', '', image["name"].lower())
            if not base_name:
                base_name = generate_image_slug(image["prompt"], i + 1)

        # Handle duplicate names by appending counter
        if base_name in used_names:
            used_names[base_name] += 1
            image["name"] = f"{base_name}_{used_names[base_name]}"
        else:
            used_names[base_name] = 1
            image["name"] = base_name

        # Validate optional fields
        if "aspect_ratio" in image and image["aspect_ratio"] not in ASPECT_RATIO_WHITELIST:
            raise ValueError(f"Image {i} aspect_ratio must be one of {ASPECT_RATIO_WHITELIST}")

        if "resolution" in image and image["resolution"] not in RESOLUTION_WHITELIST:
            raise ValueError(f"Image {i} resolution must be one of {RESOLUTION_WHITELIST}")

        # Validate global_style_references if present
        if "global_style_references" in image:
            if not isinstance(image["global_style_references"], list):
                raise ValueError(f"Image {i} global_style_references must be a list")

    return data


def parse_mode(input_file, output_file):
    """Parse natural language file to YAML using Gemini structured output."""

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    with open(input_file, "r") as f:
        user_input = f.read().strip()

    if not user_input:
        print("Error: Input file is empty")
        sys.exit(1)

    print(f"Parsing {input_file}...")

    # Create the Gemini schema
    schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "images": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING),
                        "prompt": types.Schema(type=types.Type.STRING),
                        "variations": types.Schema(type=types.Type.INTEGER),
                        "aspect_ratio": types.Schema(type=types.Type.STRING),
                        "resolution": types.Schema(type=types.Type.STRING),
                    },
                    required=["prompt", "variations"],
                ),
            ),
            "global_style_references": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
            ),
            "output_folder": types.Schema(type=types.Type.STRING),
        },
        required=["images"],
    )

    try:
        response = client.models.generate_content(
            model=PARSE_MODEL,
            contents=f"""Parse this natural language request into a batch image generation YAML structure.

For each image request:
- Extract a clear, descriptive prompt
- Default to 4 variations if not specified, but cap at maximum 4 variations
- Map terms like "widescreen"→"16:9", "portrait"→"9:16"
- Extract any file paths for style references

Return valid JSON matching this structure:
{{
  "images": [
    {{"prompt": "description", "variations": 4, "aspect_ratio": "16:9"}},
    ...
  ],
  "global_style_references": []
}}

User request:
{user_input}""",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        # Parse the JSON response
        response_text = response.text
        if not response_text:
            raise ValueError("Empty response from Gemini")
        parsed_data = json.loads(response_text)

        # Validate and apply defaults
        validated_data = validate_yaml(parsed_data)

        # Track if any were capped
        capped_count = 0
        total_images = 0

        for image in validated_data["images"]:
            variations = image.get("variations", 4)
            total_images += variations
            if variations > MAX_VARIATIONS:
                capped_count += 1

        # Generate output folder path based on input file name
        output_folder_name = get_output_folder_name(input_file)
        output_folder_dir = os.path.dirname(os.path.abspath(output_file))
        output_folder_path = os.path.join(output_folder_dir, output_folder_name)

        # Add output folder to YAML
        validated_data["output_folder"] = output_folder_path

        # Save as YAML
        with open(output_file, "w") as f:
            yaml.dump(validated_data, f, default_flow_style=False, sort_keys=False)

        # Display summary
        print(f"\nParsed successfully!")
        print(f"Will generate {total_images} images from {len(validated_data['images'])} prompts:")

        for i, image in enumerate(validated_data["images"], 1):
            prompt = image["prompt"]
            variations = image["variations"]
            name = image["name"]
            extra_info = ""

            # Check if this was capped
            original_variations = parsed_data["images"][i-1].get("variations", 4)
            if original_variations > MAX_VARIATIONS:
                extra_info = f", capped from {original_variations}"

            if "aspect_ratio" in image:
                extra_info += f", {image['aspect_ratio']}"

            print(f"  • \"{prompt}\" ({variations} variations{extra_info})")
            print(f"    → Files: {name}_001.png, {name}_002.png, ..." if variations > 1 else f"    → File: {name}_001.png")

        print(f"\nSaved to: {output_file}")
        print(f"Ready to generate! Run: uv run generate.py {output_file}")

    except ClientError as e:
        if "429" in str(e):
            print("Error: API quota exceeded")
            print("\nYour free tier quota is exhausted. To continue:")
            print("1. Upgrade to a paid plan: https://ai.google.dev/pricing")
            print("2. Or wait for your quota to reset (daily limit)")
            sys.exit(1)
        else:
            print(f"Error during parsing: {e}")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse Gemini response as JSON: {e}")
        sys.exit(1)


def generate_image(prompt, output_dir, filename, aspect_ratio=None, resolution=None):
    """Generate a single image and save it directly to output directory.

    Args:
        prompt: The image generation prompt
        output_dir: Output directory (flat structure, no subdirs)
        filename: Full filename including .png extension
        aspect_ratio: Optional aspect ratio (e.g., "16:9")
        resolution: Optional resolution (e.g., "2K")

    Returns:
        Dict with status, filename, and optional error
    """

    try:
        # Build request
        request_content = prompt

        if aspect_ratio or resolution:
            # Build generation config if aspect ratio or resolution specified
            config_parts = []
            if aspect_ratio:
                config_parts.append(f"aspect_ratio: {aspect_ratio}")
            if resolution:
                config_parts.append(f"quality: {resolution}")

            request_content = f"{prompt}\n\n[{', '.join(config_parts)}]"

        response = client.models.generate_content(
            model=GENERATE_MODEL,
            contents=request_content,
        )

        # Extract and save the image
        if response.parts:
            for part in response.parts:
                if part.inline_data and part.inline_data.data:
                    image_data = part.inline_data.data

                    # Save image directly to output_dir with the provided filename
                    image_path = os.path.join(output_dir, filename)
                    with open(image_path, "wb") as f:
                        f.write(image_data)

                    return {"status": "success", "filename": filename}

        return {"status": "failed", "error": "No image data in response"}

    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            return {"status": "failed", "error": "Rate limit exceeded", "rate_limited": True}
        return {"status": "failed", "error": error_str}


def generate_mode(yaml_file):
    """Generate images from YAML batch file."""

    if not os.path.exists(yaml_file):
        print(f"Error: YAML file '{yaml_file}' not found")
        sys.exit(1)

    # Load and validate YAML
    try:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        validated_data = validate_yaml(data)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine output directory
    if "output_folder" in validated_data:
        output_dir = validated_data["output_folder"]
    else:
        # Fallback: generate from yaml filename if not in file
        output_folder_name = get_output_folder_name(yaml_file)
        yaml_dir = os.path.dirname(os.path.abspath(yaml_file))
        output_dir = os.path.join(yaml_dir, output_folder_name)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Calculate total images and prepare metadata tracking
    total_images = sum(img.get("variations", 4) for img in validated_data["images"])

    print(f"Generating {total_images} images from {len(validated_data['images'])} prompts...")

    # Track all generated images and update validated_data with results
    image_counter = 1
    rate_limited = False

    for image_config in validated_data["images"]:
        prompt = image_config["prompt"]
        name = image_config["name"]
        variations = image_config.get("variations", 4)
        aspect_ratio = image_config.get("aspect_ratio")
        resolution = image_config.get("resolution")

        # Initialize generated list for this image config
        if "generated" not in image_config:
            image_config["generated"] = []

        for variation_num in range(1, variations + 1):
            # Generate filename: {name}_{001}.png
            filename = f"{name}_{variation_num:03d}.png"

            print(f"  [{image_counter}/{total_images}] Generating {filename}...", end=" ", flush=True)

            result = generate_image(prompt, output_dir, filename, aspect_ratio, resolution)

            if result["status"] == "success":
                print("✓")
                image_config["generated"].append({
                    "file": filename,
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            else:
                print(f"✗ ({result['error']})")
                image_config["generated"].append({
                    "file": filename,
                    "status": "failed",
                    "error": result.get("error", "Unknown error"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

                if result.get("rate_limited"):
                    rate_limited = True
                    break

            image_counter += 1

        if rate_limited:
            break

    # Save output.yaml with input-compatible format + results
    output_yaml_path = os.path.join(output_dir, "output.yaml")
    with open(output_yaml_path, "w") as f:
        yaml.dump(validated_data, f, default_flow_style=False, sort_keys=False)

    # Summary
    successful = 0
    failed = 0
    for image_config in validated_data["images"]:
        for gen in image_config.get("generated", []):
            if gen["status"] == "success":
                successful += 1
            else:
                failed += 1

    total_attempted = successful + failed

    print(f"\n{'='*50}")
    print(f"Generation complete!")
    print(f"  Successful: {successful}/{total_attempted}")
    if failed > 0:
        print(f"  Failed: {failed}/{total_attempted}")

    if rate_limited:
        print(f"\n⚠️  Rate limit exceeded. Partial results saved.")
        print(f"You can resume generation by editing {yaml_file} to remove completed images.")

    print(f"\nOutput structure:")
    print(f"  {output_dir}/")
    print(f"    ├── output.yaml               (metadata + results)")
    for image_config in validated_data["images"][:2]:  # Show first 2 as examples
        name = image_config["name"]
        variations = image_config.get("variations", 4)
        if variations == 1:
            print(f"    ├── {name}_001.png")
        else:
            print(f"    ├── {name}_001.png")
            print(f"    ├── {name}_002.png")
            if variations > 2:
                print(f"    ├── ...")
    if len(validated_data["images"]) > 2:
        print(f"    └── ...")
    else:
        print(f"    └── {validated_data['images'][-1]['name']}_001.png")

    print(f"\nMetadata saved to: {output_yaml_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch image generation with natural language parsing"
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input file (prompts.txt for parsing or batch.yaml for generation)"
    )
    parser.add_argument(
        "--parse",
        action="store_true",
        help="Parse natural language prompts to YAML"
    )
    parser.add_argument(
        "--output",
        help="Output file for parsing (required with --parse)"
    )

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    if args.parse:
        if not args.output:
            print("Error: --output is required when using --parse")
            sys.exit(1)
        parse_mode(args.input, args.output)
    else:
        generate_mode(args.input)


if __name__ == "__main__":
    main()
