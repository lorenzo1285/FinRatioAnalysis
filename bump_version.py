"""
Version Bumper for FinRatioAnalysis
Usage: python bump_version.py [major|minor|patch]
"""

import sys
import re
from pathlib import Path

def bump_version(bump_type='patch'):
    """Bump version in pyproject.toml"""
    
    pyproject_path = Path('pyproject.toml')
    content = pyproject_path.read_text()
    
    # Find current version
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        return False
    
    major, minor, patch = map(int, match.groups())
    
    # Bump version based on type
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        print(f"Error: Invalid bump type '{bump_type}'. Use: major, minor, or patch")
        return False
    
    old_version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    new_version = f"{major}.{minor}.{patch}"
    
    # Update pyproject.toml
    new_content = content.replace(
        f'version = "{old_version}"',
        f'version = "{new_version}"'
    )
    
    pyproject_path.write_text(new_content)
    
    print(f"✅ Version bumped: {old_version} → {new_version}")
    print(f"\nNext steps:")
    print(f"  1. git add pyproject.toml")
    print(f"  2. git commit -m 'Bump version to {new_version}'")
    print(f"  3. git tag v{new_version}")
    print(f"  4. git push origin main --tags")
    print(f"  5. uv build && uv publish")
    
    return True

if __name__ == '__main__':
    bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    success = bump_version(bump_type)
    sys.exit(0 if success else 1)
