# Version Management Guide

## Current Version: 0.0.7

## Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR** (1.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

---

## Quick Version Bumping

### Using the Script:

```bash
# Bump patch version (0.0.7 → 0.0.8) - for bug fixes
python bump_version.py patch

# Bump minor version (0.0.7 → 0.1.0) - for new features
python bump_version.py minor

# Bump major version (0.0.7 → 1.0.0) - for breaking changes
python bump_version.py major
```

### Manual Edit:

Edit `pyproject.toml` line 3:
```toml
version = "0.0.8"  # Change this number
```

---

## Complete Release Workflow

### Option 1: Quick Release (Manual)

```bash
# 1. Bump version
python bump_version.py patch

# 2. Commit and tag
git add pyproject.toml
git commit -m "Bump version to 0.0.8"
git tag v0.0.8
git push origin main --tags

# 3. Build and publish
uv build
uv publish
```

### Option 2: Using PowerShell Script

Create `release.ps1`:
```powershell
param([string]$Type = "patch")

# Bump version
python bump_version.py $Type

# Get new version from pyproject.toml
$version = (Select-String -Path pyproject.toml -Pattern 'version = "(.+)"').Matches.Groups[1].Value

# Git operations
git add pyproject.toml
git commit -m "Release v$version"
git tag "v$version"
git push origin main --tags

# Build and publish
uv build
uv publish

Write-Host "✅ Released version $version to PyPI!"
```

Then run:
```powershell
.\release.ps1 patch   # or minor, or major
```

---

## Version History Best Practices

### Keep a CHANGELOG.md

```markdown
# Changelog

## [0.0.8] - 2026-01-26
### Fixed
- Fixed EBIT fallback logic for financial institutions
- Removed pandas_datareader dependency
- Eliminated 56 FutureWarnings

### Added
- Support for banks (JPM, financial institutions)
- Helper methods for NaN handling
- 108 comprehensive tests

## [0.0.7] - 2025-XX-XX
### Added
- Initial release with basic ratios
```

---

## When to Bump Which Version?

### PATCH (0.0.7 → 0.0.8)
- Bug fixes
- Documentation updates
- Performance improvements
- No new features, no breaking changes

### MINOR (0.0.7 → 0.1.0)
- New features (new ratio methods)
- New optional parameters
- Deprecations (but still backward compatible)

### MAJOR (0.0.7 → 1.0.0)
- Breaking API changes
- Removing deprecated features
- Major refactoring
- Production-ready release (0.x → 1.0)

---

## Pre-release Versions

For testing before official release:

```bash
# Alpha release
version = "0.0.8a1"

# Beta release
version = "0.0.8b1"

# Release candidate
version = "0.0.8rc1"
```

Install with:
```bash
pip install FinRatioAnalysis==0.0.8a1
```

---

## Current Recommendation

Since you have:
- ✅ Major improvements (bank support, no warnings, 108 tests)
- ✅ Removed dependency (pandas_datareader)
- ✅ New features (helper methods, conditional metrics)

**Suggested next version: 0.1.0** (minor bump - significant new features)

Or if you consider it production-ready: **1.0.0** (major - first stable release)

---

## Quick Commands

```bash
# See current version
grep version pyproject.toml

# Bump and release in one go
python bump_version.py minor && git add pyproject.toml && git commit -m "Release v0.1.0" && git tag v0.1.0 && git push origin main --tags && uv build && uv publish
```
