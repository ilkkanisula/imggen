# Testing Guide for Nanobanana

Comprehensive test suite with automated tests and manual testing scenarios.

## Quick Start (5 minutes)

### Option 1: Run Automated Tests

```bash
# Install dependencies
uv pip install -r tests/test-requirements.txt

# Run all 33 tests
pytest tests/

# Expected output
============================== 33 passed in 0.86s ==============================
```

### Option 2: Try a Manual Test

```bash
# Create test input
cat > test.txt << 'EOF'
Create 2 versions of a mountain sunset
EOF

# Parse to YAML
uv run generate.py --parse test.txt --output batch.yaml

# Check output
cat batch.yaml
```

### Option 3: Full Manual Test

```bash
# Create batch file
cat > test_batch.yaml << 'EOF'
images:
  - prompt: "serene mountain landscape"
    variations: 2
  - prompt: "ocean sunset"
    variations: 2
global_style_references: []
output_folder: ./test_output
EOF

# Generate images
uv run generate.py test_batch.yaml

# Check results
ls test_output/
```

**With Style References (optional):**

```bash
# Create batch with style references
cat > test_batch_styled.yaml << 'EOF'
images:
  - prompt: "serene mountain landscape"
    variations: 2
  - prompt: "ocean sunset"
    variations: 2
global_style_references:
  - /path/to/style_image.png
output_folder: ./styled_output
EOF

# Generate with consistent styling
uv run generate.py test_batch_styled.yaml
```

## Test Coverage

### Automated Tests (33 tests)
- **YAML Validation** (12 tests): Schema validation, defaults, constraints
- **Parse Mode** (4 tests): Natural language parsing, error handling
- **Image Generation** (4 tests): Single image generation, aspect ratios
- **Batch Generation** (6 tests): Batch processing, manifest creation
- **Integration** (1 test): Complete parse → generate workflow
- **Edge Cases** (4 tests): Boundary values, special characters, large batches
- **Output Format** (2 tests): YAML validity, field preservation

### Manual Testing (15 scenarios)
See `MANUAL_TESTING.md` for detailed step-by-step scenarios including:
- Parse mode tests (3 scenarios)
- Generate mode tests (4 scenarios)
- Error handling (5 scenarios)
- Validation (2 scenarios)
- End-to-end workflow (1 scenario)

## Running Tests

### All Tests
```bash
pytest tests/
```

### Specific Test Class
```bash
pytest tests/test_generate.py::TestValidateYaml
pytest tests/test_generate.py::TestParseMode
pytest tests/test_generate.py::TestGenerateImage
pytest tests/test_generate.py::TestGenerateMode
```

### Specific Test
```bash
pytest tests/test_generate.py::TestValidateYaml::test_valid_simple_yaml
```

### With Verbose Output
```bash
pytest -v tests/
```

### With Coverage Report
```bash
pytest --cov=generate --cov-report=html tests/
```

### Run Tests by Keyword
```bash
pytest -k "validate"       # All validation tests
pytest -k "parse"          # All parse tests
pytest -k "rate_limit"     # All rate limit tests
```

## Test Dependencies

Required packages:
- `pytest>=7.0` - Test framework
- `pyyaml>=6.0` - YAML parsing

Install with:
```bash
uv pip install -r tests/test-requirements.txt
```

Or manually:
```bash
uv pip install pytest pyyaml
```

## Test Code Organization

### test_generate.py (647 lines)
8 test classes with 33 automated tests:

| Class | Tests | Coverage |
|-------|-------|----------|
| TestValidateYaml | 12 | YAML schema validation |
| TestParseMode | 4 | Natural language parsing |
| TestGenerateImage | 4 | Single image generation |
| TestGenerateMode | 6 | Batch generation |
| TestIntegration | 1 | End-to-end workflow |
| TestEdgeCases | 4 | Boundary conditions |
| TestYamlOutputFormat | 2 | Output validity |

### conftest.py (114 lines)
Pytest fixtures for reusable test setup:

- `temp_dir` - Temporary test directory
- `sample_prompts_file` - Natural language prompts
- `sample_batch_yaml` - YAML batch configuration
- `sample_image_data` - Valid PNG image bytes
- `mock_gemini_client` - Mocked Gemini API
- `output_dir` - Generated images directory
- `monkeypatch_output_dir` - OUTPUT_DIR monkeypatch

## Manual Testing

For detailed manual testing scenarios (setup, execution, verification steps):
→ See `MANUAL_TESTING.md`

15 scenarios covering:
- Parse mode with simple/complex batches
- Generate mode with various options
- Error handling and validation
- Rate limit handling
- End-to-end workflows

## Directory Structure

```
tests/
├── docs/               ← This documentation
│   ├── README.md      (this file)
│   └── MANUAL_TESTING.md (manual test scenarios)
├── test_generate.py    (33 automated test cases)
├── conftest.py         (pytest fixtures)
├── pytest.ini          (pytest configuration)
├── test-requirements.txt (dependencies)
└── __init__.py
```

## Troubleshooting

### "pytest not found"
```bash
uv pip install -r tests/test-requirements.txt
```

### "ModuleNotFoundError: No module named 'google'"
```bash
uv pip install google-genai python-dotenv
```

### "GOOGLE_API_KEY not set"
```bash
# Automated tests use mocking, no API key needed
export GOOGLE_API_KEY=test_key
pytest tests/

# Manual tests need real API key
echo "GOOGLE_API_KEY=your_actual_key" > .env
```

### Tests fail with "Rate limited"
- Automated tests use mocking, no rate limits
- Manual tests may hit API limits (50 requests/day free tier)
- Upgrade: https://aistudio.google.com/app/billing/overview

## Test Statistics

| Metric | Value |
|--------|-------|
| Automated Tests | 33 |
| Manual Scenarios | 15 |
| Test Classes | 8 |
| Fixtures | 7 |
| Execution Time | ~0.8s |
| Documentation Lines | ~850 |

## Key Features

✓ **No Real API Calls** - Automated tests use mocking
✓ **Fast Execution** - All 33 tests run in <1 second
✓ **Complete Coverage** - YAML validation, parsing, generation, errors
✓ **Manual Scenarios** - 15 detailed step-by-step test cases
✓ **Self-Contained** - All test files in single directory
✓ **Well-Documented** - This README + manual testing guide

## Related Documentation

- **Main README:** `../../README.md` - Project overview
- **Batch & Variations Spec:** `../../specs/batch-and-variations.md`
- **Implementation:** `../../generate.py` - Source code
- **Manual Testing:** `MANUAL_TESTING.md` - 15 detailed test scenarios

---

**Status:** ✅ 33 automated tests passing | ✅ 15 manual scenarios documented
