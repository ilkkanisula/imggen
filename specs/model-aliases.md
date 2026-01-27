# Model Aliases Spec

## Problem

`--model google` and `--model openai` don't work as expected. The `infer_provider_from_model()` function only matches prefixes (`gemini-`, `google-`, `gpt-`, `dall-e-`), so bare provider names fall through to the default (OpenAI).

## Solution

Recognize `"google"` and `"openai"` as model aliases that resolve to each provider's current default model.

## Alias Mapping

| Alias    | Resolves To                    |
|----------|--------------------------------|
| `google` | `gemini-3-pro-image-preview`   |
| `openai` | `gpt-image-1.5`               |

## Changes

### `src/imggen/providers/__init__.py`

In `infer_provider_from_model()`, add exact match for bare provider names before prefix matching:

- `"google"` → return `"google"`
- `"openai"` → return `"openai"`

### `src/imggen/cli.py`

After provider inference, resolve alias to actual model name before passing to `generate_from_prompt()`. Use the provider's `get_generate_model()` to get the default model when a bare alias is used.

### `src/imggen/cli.py` help text

Update `--model` help to mention aliases: `"Model name or alias (google, openai). Default: gpt-image-1.5"`

## Tests

### `tests/test_providers.py`

- `test_infer_from_bare_provider_name`: verify `"google"` → `"google"`, `"openai"` → `"openai"` (already added)

### `tests/test_cli.py`

- Verify `--model google` results in Google provider and `gemini-3-pro-image-preview` model
- Verify `--model openai` results in OpenAI provider and `gpt-image-1.5` model

## CLI Usage

```bash
# These become equivalent:
imggen -p "landscape" --model google
imggen -p "landscape" --model gemini-3-pro-image-preview

imggen -p "landscape" --model openai
imggen -p "landscape" --model gpt-image-1.5
```
