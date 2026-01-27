# Publishing to PyPI Guide

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **Version Bump**: Update version in `pyproject.toml` before each release (currently 0.0.7)

## Method 1: Manual Publishing with uv (Immediate)

### Step 1: Build the Package
```bash
# Clean old builds (if any)
rm -r dist/ build/ *.egg-info

# Build distribution with uv
uv build
```

This creates:
- `dist/FinRatioAnalysis-0.0.7-py3-none-any.whl` (wheel)
- `dist/FinRatioAnalysis-0.0.7.tar.gz` (source)

### Step 2: Upload to PyPI
```bash
# Upload to PyPI
uv publish
```

You'll be prompted for:
- Username: Your PyPI username
- Password: Your PyPI password (or API token)

**Using API Token (Recommended):**
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Use `__token__` as username
4. Use the token (starts with `pypi-`) as password

**Or set environment variables:**
```bash
# PowerShell
$env:UV_PUBLISH_USERNAME = "__token__"
$env:UV_PUBLISH_PASSWORD = "pypi-your-token-here"
uv publish
```

---

## Method 2: Automated GitHub Actions (Better for Future Releases)

### Setup (One-time):

1. **Configure Trusted Publishing on PyPI:**
   - Go to https://pypi.org/manage/project/FinRatioAnalysis/settings/
   - Click "Publishing" → "Add a new publisher"
   - Fill in:
     - PyPI Project Name: `FinRatioAnalysis`
     - Owner: `lorenzo1285`
     - Repository name: `FinRatioAnalysis`
     - Workflow name: `publish-to-pypi.yml`
     - Environment name: `pypi`

2. **Create GitHub Environment:**
   - Go to your repo → Settings → Environments
   - Create new environment named `pypi`
   - Add protection rules if desired

### Usage (Every Release):

1. **Update Version:**
   ```bash
   # Edit pyproject.toml, change version to 0.0.8 (or next version)
   ```

2. **Commit and Push:**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.0.8"
   git push origin main
   ```

3. **Create GitHub Release:**
   - Go to https://github.com/lorenzo1285/FinRatioAnalysis/releases/new
   - Tag: `v0.0.8`
   - Title: `v0.0.8 - Description of changes`
   - Description: List changes/improvements
   - Click "Publish release"

4. **Automatic Publishing:**
   - GitHub Actions will automatically build and publish to PyPI
   - Check progress: Actions tab in your repository

---

## Quick Start for NEXT Release

### Recommended Workflow:

```bash
# 1. Update version in pyproject.toml
# Change: version = "0.0.8"

# 2. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.0.8: Major improvements"
git push origin main

# 3. Create GitHub release
# - Go to GitHub → Releases → New Release
# - Tag: v0.0.8
# - Publish

# 4. Wait for Actions to complete
# Package automatically published to PyPI!
```

---

## For THIS Release (v0.0.7) - Quick Steps with uv:

```bash
# Build package
uv build

# Upload to PyPI (you'll need PyPI credentials)
uv publish
```

---

## Testing Before Publishing

### Test on TestPyPI first:
```bash
# Build package
uv build

# Upload to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ FinRatioAnalysis
```

---

## Checklist Before Publishing

- [ ] All tests pass (108/108)
- [ ] Version bumped in pyproject.toml
- [ ] README.md updated
- [ ] CHANGELOG or release notes prepared
- [ ] No sensitive data in code
- [ ] Dependencies listed correctly
- [ ] License file present (MIT)

---

## Common Issues

**"File already exists"**: You can't re-upload the same version. Bump version number.

**Authentication failed**: Use API token instead of password.

**Build fails**: Make sure `pyproject.toml` has correct format.
