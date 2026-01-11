# Test Organization

Tests follow Core Patterns (Factory Pattern, Separation of Concerns, Pre-flight Validation, Fail Fast). Each module has a dedicated test file with no mixed concerns.

## Quick Commands

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_cli.py -v

# Count tests
uv run pytest tests/ --collect-only -q
```

## Test Organization

| Module | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| `providers/__init__.py` | `test_providers.py` | 10 | Factory, inference, interface |
| `config.py` | `test_config.py` | 6 | Config migration, multi-key support |
| `pricing.py` | `test_pricing.py` | 10 | Cost calculations for all providers |
| `generator.py` | `test_generator.py` | 4 | File collision detection |
| `cli.py` | `test_cli.py` | 34 | Argument validation, prompt/reference loading |
| **Total** | **5 files** | **64 tests** | **100% of modules** |

## Test Files

### test_providers.py (10 tests)
Provider factory pattern and interface tests.
- `TestProviderFactory` - Create Google and OpenAI providers
- `TestProviderInference` - Infer provider from model name
- `TestProviderInterface` - Verify required methods

### test_config.py (6 tests)
Configuration management and multi-provider API key support.
- `TestConfigMigration` - Old format → new format
- `TestMultiProviderConfig` - Multi-provider API key storage

### test_pricing.py (10 tests)
Cost calculations for all providers and quality/resolution settings.
- `TestPricingCalculations` - OpenAI quality levels, Google resolutions

### test_generator.py (4 tests)
Image generation orchestration and pre-flight validation.
- `TestFileCollisionDetection` - Prevent file overwrites before API calls

### test_cli.py (34 tests)
CLI argument parsing and validation (Fail Fast pattern).
- `TestPromptLoading` (7 tests) - Load from text or file
- `TestReferenceLoading` (7 tests) - Load reference images
- `TestArgumentValidation` (20 tests) - Aspect ratio, quality, resolution, variations

## Feature-to-Test Mapping

| Feature | Test File(s) | Test Class |
|---------|-------------|-----------|
| Image generation from prompts | test_generator.py, test_cli.py | TestPromptLoading, TestGenerateImage |
| Multiple variations | test_generator.py, test_pricing.py | TestGenerateImage, TestPricingCalculations |
| Reference image support | test_cli.py | TestReferenceLoading |
| Quality/resolution options | test_pricing.py, test_cli.py | TestPricingCalculations, TestArgumentValidation |
| Aspect ratio control | test_cli.py | TestArgumentValidation |
| Multiple providers | test_providers.py, test_pricing.py | TestProviderFactory, TestPricingCalculations |
| Cost estimation | test_pricing.py, test_generator.py | TestPricingCalculations |
| API key management | test_config.py | TestConfigMigration, TestMultiProviderConfig |
| File collision prevention | test_generator.py | TestFileCollisionDetection |

## Verify Organization

Check test structure alignment:

```bash
# 1. No duplicate test names
grep -r "def test_" tests/ | cut -d: -f2 | sort | uniq -d

# 2. Total test count (should be 64)
uv run pytest tests/ --collect-only -q

# 3. All test files exist
ls -la tests/test_*.py

# 4. Module → test file mapping
for file in src/imggen/{cli,config,generator,pricing}.py src/imggen/providers/__init__.py; do
  module=$(basename $file .py)
  test_file="tests/test_${module}.py"
  if [ -f "$test_file" ]; then echo "✓ $test_file"; else echo "✗ $test_file"; fi
done
```

## When Adding New Features

1. **Find related tests** - Check which test file covers the feature area
2. **Add TDD test first** - Write test in that test file before implementation
3. **Run that test file** - `uv run pytest tests/test_<module>.py -v`
4. **Implement** - Add feature code
5. **Run all tests** - Ensure no regressions
