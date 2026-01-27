# Quick Publishing Guide

## Setup (One-time)

1. Get your PyPI API token from: https://pypi.org/manage/account/token/
2. Edit `.env` file and replace `pypi-your-token-here` with your actual token
3. The `.env` file is already in `.gitignore` so it won't be committed

## Publish to PyPI

```powershell
# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

# Build and publish
uv build
uv publish
```

Or simply:

```powershell
# One command (loads .env automatically if configured)
uv publish
```

## Test First (Optional)

```powershell
# Publish to TestPyPI first
uv publish --publish-url https://test.pypi.org/legacy/

# Install and test
pip install --index-url https://test.pypi.org/simple/ FinRatioAnalysis
```

## After Publishing

Package will be available at: https://pypi.org/project/FinRatioAnalysis/

Users can install with:
```bash
pip install FinRatioAnalysis
```
