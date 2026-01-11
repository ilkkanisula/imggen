# Manual Testing Guide

This guide provides step-by-step instructions for manually testing the batch and variations functionality without running automated tests.

## Prerequisites

1. **API Key Setup**
   ```bash
   # Ensure .env file has valid GOOGLE_API_KEY
   cat .env
   # Output: GOOGLE_API_KEY=your_actual_key_here
   ```

2. **Required Files**
   ```bash
   # Verify you're in the project root
   pwd  # Should show: /Users/ilkkanisula/work/ai/tools/nanobanana

   # Check files exist
   ls -la generate.py
   ```

## Manual Test 1: Parse Mode - Simple Batch

### Setup
```bash
# Create a simple prompts file
cat > manual_test_prompts.txt << 'EOF'
Create 2 versions of a sunset over mountains

I need 3 variations of a futuristic city
EOF
```

### Execute Parse Mode
```bash
uv run generate.py --parse manual_test_prompts.txt --output manual_test_batch.yaml
```

### Expected Output
```
Parsing manual_test_prompts.txt...

Parsed successfully!
Will generate 5 images from 2 prompts:
  • "sunset over mountains" (2 variations)
  • "futuristic city" (3 variations)

Saved to: manual_test_batch.yaml
Ready to generate! Run: uv run generate.py manual_test_batch.yaml
```

### Verify
```bash
# Check the generated YAML file
cat manual_test_batch.yaml
```

Expected YAML structure:
```yaml
images:
  - prompt: "sunset over mountains"
    variations: 2
  - prompt: "futuristic city"
    variations: 3
global_style_references: []
```

---

## Manual Test 2: Parse Mode - Variations Capping

### Setup
```bash
# Create prompts requesting more than 4 variations
cat > manual_test_cap_prompts.txt << 'EOF'
Generate 10 versions of a landscape

I need 8 different variations of a portrait
EOF
```

### Execute Parse Mode
```bash
uv run generate.py --parse manual_test_cap_prompts.txt --output manual_test_cap_batch.yaml
```

### Expected Output
Should show capping warnings:
```
Parsed successfully!
Will generate 8 images from 2 prompts:
  • "landscape" (4 variations, capped from 10)
  • "portrait" (4 variations, capped from 8)

Saved to: manual_test_cap_batch.yaml
```

### Verify
```bash
cat manual_test_cap_batch.yaml
# Both should have variations: 4 (capped)
```

---

## Manual Test 3: Generate Mode - Basic Batch

### Setup
Create a YAML batch file:
```bash
cat > manual_test_generate.yaml << 'EOF'
images:
  - prompt: "a serene mountain landscape at sunset"
    variations: 2

global_style_references: []
EOF
```

### Execute Generate Mode
```bash
uv run generate.py manual_test_generate.yaml
```

### Expected Output
```
Generating 2 images from 1 prompts...
  [1/2] Generating image_001... ✓
  [2/2] Generating image_002... ✓

==================================================
Generation complete!
  Successful: 2/2

Output saved to: output/
Manifest: output/batch_manifest.json
```

### Verify Output Structure
```bash
# Check output directory structure
tree output/
# OR
find output/ -type f

# Should show:
# output/image_001/image.png
# output/image_001/prompt.txt
# output/image_002/image.png
# output/image_002/prompt.txt
# output/batch_manifest.json
```

### Verify Manifest
```bash
cat output/batch_manifest.json | python -m json.tool
```

Expected manifest structure:
```json
{
  "timestamp": "2024-01-08T15:30:00+00:00",
  "images": [
    {
      "id": "image_001",
      "prompt": "a serene mountain landscape at sunset",
      "status": "success",
      "output": "image.png",
      "file": "image_001/image.png"
    },
    {
      "id": "image_002",
      "prompt": "a serene mountain landscape at sunset",
      "status": "success",
      "output": "image.png",
      "file": "image_002/image.png"
    }
  ]
}
```

### Verify Saved Prompts
```bash
# Check that exact prompts are saved
cat output/image_001/prompt.txt
# Output: a serene mountain landscape at sunset

cat output/image_002/prompt.txt
# Output: a serene mountain landscape at sunset
```

---

## Manual Test 4: Generate Mode - Multiple Prompts

### Setup
Create a complex YAML with multiple images:
```bash
cat > manual_test_multi.yaml << 'EOF'
images:
  - prompt: "a snowy mountain peak"
    variations: 2
  - prompt: "tropical beach sunset"
    variations: 2
  - prompt: "forest waterfall"
    variations: 1

global_style_references: []
EOF
```

### Execute Generate Mode
```bash
uv run generate.py manual_test_multi.yaml
```

### Expected Output
```
Generating 5 images from 3 prompts...
  [1/5] Generating image_001... ✓
  [2/5] Generating image_002... ✓
  [3/5] Generating image_003... ✓
  [4/5] Generating image_004... ✓
  [5/5] Generating image_005... ✓

==================================================
Generation complete!
  Successful: 5/5

Output saved to: output/
Manifest: output/batch_manifest.json
```

### Verify
```bash
# Check all images were created
ls -la output/image_*

# Verify manifest has 5 images
cat output/batch_manifest.json | grep '"id"' | wc -l
# Should output: 5
```

---

## Manual Test 5: Generate Mode - With Aspect Ratios

### Setup
Create YAML with aspect ratio specifications:
```bash
cat > manual_test_aspect.yaml << 'EOF'
images:
  - prompt: "widescreen mountain view"
    variations: 1
    aspect_ratio: "16:9"
  - prompt: "portrait-style landscape"
    variations: 1
    aspect_ratio: "9:16"
  - prompt: "square composition"
    variations: 1
    aspect_ratio: "1:1"

global_style_references: []
EOF
```

### Execute Generate Mode
```bash
uv run generate.py manual_test_aspect.yaml
```

### Expected Output
Should show 3 images generated successfully with aspect ratios applied.

### Verify
```bash
# Check manifest for aspect ratios
cat output/batch_manifest.json | python -m json.tool
```

---

## Manual Test 6: Error Handling - Invalid YAML

### Setup
Create an invalid YAML file:
```bash
cat > manual_test_invalid.yaml << 'EOF'
invalid: yaml: content: [
images:
  - missing_prompt: "test"
EOF
```

### Execute Generate Mode
```bash
uv run generate.py manual_test_invalid.yaml
```

### Expected Output
```
Error: Invalid YAML file: mapping values are not allowed here
  in "manual_test_invalid.yaml", line 1, column 13
```

---

## Manual Test 7: Error Handling - Missing Images Key

### Setup
```bash
cat > manual_test_no_images.yaml << 'EOF'
global_style_references: []
EOF
```

### Execute Generate Mode
```bash
uv run generate.py manual_test_no_images.yaml
```

### Expected Output
```
Error: YAML must contain 'images' key with list of image configs
```

---

## Manual Test 8: Error Handling - Empty Prompt

### Setup
```bash
cat > manual_test_empty_prompt.yaml << 'EOF'
images:
  - prompt: ""
    variations: 2

global_style_references: []
EOF
```

### Execute Generate Mode
```bash
uv run generate.py manual_test_empty_prompt.yaml
```

### Expected Output
```
Error: Image 0 must have a non-empty 'prompt'
```

---

## Manual Test 9: File Not Found - Parse Mode

### Execute
```bash
uv run generate.py --parse /nonexistent/file.txt --output batch.yaml
```

### Expected Output
```
Error: Input file '/nonexistent/file.txt' not found
```

---

## Manual Test 10: File Not Found - Generate Mode

### Execute
```bash
uv run generate.py /nonexistent/batch.yaml
```

### Expected Output
```
Error: YAML file '/nonexistent/batch.yaml' not found
```

---

## Manual Test 11: Parse → Generate Workflow

### Complete End-to-End Test
```bash
# Step 1: Create natural language prompts
cat > workflow_prompts.txt << 'EOF'
Create 3 versions of a mountain landscape

Generate 2 variations of an ocean sunset
EOF

# Step 2: Parse to YAML
uv run generate.py --parse workflow_prompts.txt --output workflow_batch.yaml

# Step 3: Review the generated YAML
echo "=== Generated YAML ==="
cat workflow_batch.yaml

# Step 4: Generate images
uv run generate.py workflow_batch.yaml

# Step 5: Verify output
echo "=== Output Structure ==="
find output/ -type f | sort

echo "=== Manifest Content ==="
cat output/batch_manifest.json | python -m json.tool
```

### Expected Flow
1. Parse creates YAML with 5 images (3+2)
2. Generate creates 5 image directories with PNG and prompt.txt files
3. Manifest contains all 5 images with success status
4. Each prompt.txt matches the batch.yaml prompts exactly

---

## Manual Test 12: Aspect Ratio Validation

### Setup - Invalid Aspect Ratio
```bash
cat > manual_test_bad_aspect.yaml << 'EOF'
images:
  - prompt: "test image"
    aspect_ratio: "invalid:ratio"

global_style_references: []
EOF
```

### Execute
```bash
uv run generate.py manual_test_bad_aspect.yaml
```

### Expected Output
```
Error: Image 0 aspect_ratio must be one of ['1:1', '16:9', '9:16', '4:3', '3:4']
```

### Setup - Valid Aspect Ratios
Test each valid ratio individually:
```bash
for ratio in "1:1" "16:9" "9:16" "4:3" "3:4"; do
  cat > manual_test_ratio_$ratio.yaml << EOF
images:
  - prompt: "test with ratio $ratio"
    variations: 1
    aspect_ratio: "$ratio"
global_style_references: []
EOF
  echo "Testing $ratio..."
done
```

---

## Manual Test 13: Resolution Validation

### Setup - Invalid Resolution
```bash
cat > manual_test_bad_res.yaml << 'EOF'
images:
  - prompt: "test image"
    resolution: "8K"

global_style_references: []
EOF
```

### Execute
```bash
uv run generate.py manual_test_bad_res.yaml
```

### Expected Output
```
Error: Image 0 resolution must be one of ['1K', '2K', '4K']
```

### Setup - Valid Resolutions
```bash
for res in "1K" "2K" "4K"; do
  cat > manual_test_res_$res.yaml << EOF
images:
  - prompt: "test with resolution $res"
    variations: 1
    resolution: "$res"
global_style_references: []
EOF
  echo "Testing $res..."
done
```

---

## Manual Test 14: Large Batch

### Setup
Generate a batch with many images:
```bash
python3 << 'EOF'
images = []
for i in range(20):
    images.append({
        'prompt': f'image_{i:02d} description',
        'variations': 1
    })

import yaml
with open('manual_test_large_batch.yaml', 'w') as f:
    yaml.dump({'images': images, 'global_style_references': []}, f)

print(f"Created batch with {len(images)} images")
EOF
```

### Execute
```bash
time uv run generate.py manual_test_large_batch.yaml
```

### Verify
```bash
# Check all 20 images were created
ls output/image_* | wc -l
# Should be: 20

# Verify manifest
cat output/batch_manifest.json | python -m json.tool | grep '"id"' | wc -l
# Should be: 20
```

---

## Manual Test 15: Cleanup Between Tests

### After Each Test
```bash
# Remove test output
rm -rf output/

# Remove test files (except specs/)
rm -f manual_test_*.yaml
rm -f manual_test_*.txt
rm -f workflow_*.yaml
rm -f workflow_*.txt
```

### Clean Up All Manual Tests
```bash
# Safe cleanup script
rm -f manual_test_*.yaml
rm -f manual_test_*.txt
rm -f workflow_*.yaml
rm -f workflow_*.txt
rm -rf output/
echo "Manual test files cleaned up"
```

---

## Verification Checklist

After each test, verify:

- [ ] Expected output message displayed
- [ ] Files created in correct locations
- [ ] YAML structure is valid
- [ ] Manifest JSON is well-formed
- [ ] Prompts are saved exactly as specified
- [ ] Aspect ratios applied correctly (if specified)
- [ ] No errors in output
- [ ] All image files are valid PNGs

---

## Troubleshooting Manual Tests

### Issue: "GOOGLE_API_KEY not set"
```bash
# Check .env file
cat .env

# If missing, create it
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Issue: "No such file or directory: generate.py"
```bash
# Ensure you're in the project root
pwd
cd /Users/ilkkanisula/work/ai/tools/nanobanana
```

### Issue: "ModuleNotFoundError: No module named 'google'"
```bash
# Install dependencies
uv pip install google-genai python-dotenv pyyaml
```

### Issue: API Rate Limited (429 Error)
```bash
# Wait for quota to reset (usually daily)
# Check Google API quota at: https://aistudio.google.com

# Can also upgrade to paid plan for more quota
```

### Issue: Invalid PNG Generated
- Check that the image file is not 0 bytes
- Verify the API returned actual image data
- Check API response in error logs

---

## Performance Expectations

- **Parse Mode**: 1-3 seconds (single API call)
- **Generate Mode**: 2-5 seconds per image (depends on API latency)
- **Example**: 5 images ≈ 10-25 seconds total

---

## API Cost Notes

- Parse mode uses `gemini-2.0-flash` (very cheap)
- Generate mode uses `gemini-3-pro-image-preview` (image generation cost)
- Free tier: 50 requests/day
- Track usage at: https://aistudio.google.com/app/billing/overview

---

## Notes for Testers

1. **Don't commit generated output**: Add `output/` to `.gitignore`
2. **Save test files**: Keep YAML files to reproduce issues
3. **Document failures**: Note exact error messages and steps
4. **Test edge cases**: Try special characters, very long prompts, etc.
5. **Verify manifest**: Always check batch_manifest.json for accuracy
