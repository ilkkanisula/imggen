# Release Process

Release a new version of imggen following semantic versioning.

## Steps

1. **Update Version Files**
   - Update `pyproject.toml` version field
   - Update `__version__` in `src/imggen/version.py`

2. **Commit Version Bump**
   ```bash
   git commit -m "Bump version to X.Y.Z"
   ```

3. **Create and Push Git Tag**
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

## Critical: Always push tags to remote

Tags are required for:
- `imggen check-update` functionality
- Version management
- Release tracking

Never release without pushing tags.

## Verification

After release, verify:
```bash
git tag -l          # Local tags
git push origin main # Latest changes
imggen --version    # Verify installed version
imggen check-update # Verify tag detection
```
