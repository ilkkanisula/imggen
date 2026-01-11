# imggen

Generate images using AI providers: **OpenAI GPT Image 1.5** (default) or **Google Gemini 3 Pro Image**.

## Prerequisites

- **uv** - Python tool installer: https://docs.astral.sh/uv/getting-started/installation/
- **API Key(s)** - At least one of:
  - **OpenAI**: https://platform.openai.com/api-keys (Recommended - $0.009-0.133/image)
  - **Google**: https://aistudio.google.com/api-keys (Alternative - $0.134-0.24/image)

## Pricing Comparison

| Provider | Model | Quality | Cost/Image | Speed |
|----------|-------|---------|-----------|-------|
| **OpenAI** | GPT Image 1.5 | Low | $0.009 | Fast |
| **OpenAI** | GPT Image 1.5 | Medium | $0.034 | Very Fast |
| **OpenAI** | GPT Image 1.5 | High | $0.133 | Very Fast |
| **Google** | Gemini 3 Pro Image | 1K | $0.134 | Standard |
| **Google** | Gemini 3 Pro Image | 2K | $0.134 | Standard |
| **Google** | Gemini 3 Pro Image | 4K | $0.24 | Standard |

**Default:** OpenAI GPT Image 1.5 (medium quality)

## Quick Start

```bash
# 1. Install imggen
uv tool install git+https://github.com/ilkkanisula/imggen.git

# 2. Generate an image (prompts for API key on first run)
imggen -p "a serene mountain landscape at sunset"

# Done! Check your current directory for imggen_001.png

# 3. Generate multiple variations
imggen -p "cozy winter cabin" --variations 4 --output ./images/

# 4. Use a prompt file
imggen -f prompt.txt --output ./images/

# 5. Add reference images
imggen -p "portrait in style of" ref1.jpg ref2.jpg --output ./images/

# 6. Use a different provider
imggen -p "landscape" --provider google --resolution 4K --output ./images/
```

---

## How It Works

```
Direct CLI invocation
    ↓
[VALIDATE] Check arguments & file collisions
    ↓
[GENERATE] API creates images directly
    ↓
./images/ (generated files)
```

---

## Installation

```bash
uv tool install git+https://github.com/ilkkanisula/imggen.git
```

### API Key Setup

Configure your API keys interactively:

```bash
imggen setup
# =================================
# Configure Google/Gemini API:
# Get your key from: https://aistudio.google.com/api-keys
# Enter your Google API key (or press Enter to skip): [optional]
#
# Configure OpenAI API:
# Get your key from: https://platform.openai.com/api-keys
# Enter your OpenAI API key (or press Enter to skip): [required]
# ✓ Setup complete!
# ✓ Config saved to ~/.config/imggen/config.json
```

Keys are stored in `~/.config/imggen/config.json`:
```json
{
  "api_keys": {
    "openai": "sk-...",
    "google": "AIzaSy..."
  },
  "default_provider": "openai"
}
```

---

## CLI Usage

### Basic Generation

```bash
# Minimal: single image with default settings
imggen -p "a serene mountain landscape"

# Multiple variations
imggen -p "cozy winter cabin" --variations 4

# Save to specific directory (created if doesn't exist)
imggen -p "portrait" --output ./images/

# Dry run: see estimated cost without generating
imggen -p "landscape" --variations 4 --dry-run
```

### Prompt Sources

```bash
# Inline prompt
imggen -p "your prompt here"

# From file
imggen -f prompt.txt

# From file with reference images
imggen -f prompt.txt ref1.jpg ref2.jpg --output ./images/
```

### Provider & Quality Options

```bash
# Default (OpenAI, medium quality)
imggen -p "landscape"

# OpenAI with high quality
imggen -p "landscape" --quality high

# Google with 4K resolution
imggen -p "landscape" --provider google --resolution 4K

# Auto-detect provider from model
imggen -p "landscape" --model gpt-image-1.5
imggen -p "landscape" --model gemini-3-pro-image-preview
```

### Aspect Ratios

```bash
# Available ratios: 1:1, 16:9, 9:16, 4:3, 3:4 (default: 1:1)
imggen -p "landscape" --aspect-ratio 16:9
```

### Reference Images

```bash
# Positional arguments
imggen -p "portrait" ref1.jpg ref2.jpg --output ./images/

# From file (one path per line)
imggen -p "portrait" -r references.txt --output ./images/
```

### Output

```
./images/
├── imggen_001.png
├── imggen_002.png
├── imggen_003.png
└── imggen_004.png
```

**File naming:**
- Sequential numbering: `imggen_001.png`, `imggen_002.png`, etc.
- Never overwrites existing files (fails with helpful error)
- Suggests creating new output directory or deleting existing files

---

## Commands

### Main Commands

```bash
# Generate images
imggen -p "prompt"
imggen -f prompt.txt
imggen -p "prompt" --output ./images/ --variations 4

# Dry run (cost estimation only)
imggen -p "prompt" --dry-run
```

### Utility Commands

```bash
# Show version
imggen --version

# Check for updates
imggen check-update

# Update to latest version (downloads from git)
imggen update

# Interactive API key setup
imggen setup

# Show help
imggen --help
```

---

## Advanced

### Provider Selection

Choose which AI provider to use for each image:

**Set default provider (global):**
Edit `~/.config/imggen/config.json`:
```json
{
  "default_provider": "openai"  // or "google"
}
```

**Using OpenAI (Recommended):**
- Default provider
- Faster generation (up to 4x faster than Google)
- Better instruction following
- More cost-effective ($0.009-0.133/image)
- Models: `gpt-image-1.5` (latest)

**Using Google:**
- Alternative provider
- Reliable image generation
- Higher resolution options (up to 4K)
- Models: `gemini-3-pro-image-preview`
- Higher cost ($0.134-0.24/image)

---

## Troubleshooting

**Need to change API key?**
```bash
imggen setup
# or edit directly
nano ~/.config/imggen/config.json
```

**Update available?**
```bash
imggen check-update
# Then run:
imggen update
# or use uv directly:
uv tool install --upgrade git+https://github.com/ilkkanisula/imggen.git
```

**Rate limited?**
Remove completed images from `batch.yaml` and run again.

**Command not found?**
```bash
# Ensure uv tools are in PATH
uv tool update-shell

# Or manually add to ~/.zshrc or ~/.bashrc:
export PATH="$HOME/.local/bin:$PATH"
```

---

## Free Tier Limits

- 15 images/minute
- 1,500 images/day
