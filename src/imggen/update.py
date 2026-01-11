"""Update command for imggen"""

import subprocess
import sys


def update_imggen():
    """Update imggen to latest version from git."""
    print("Updating imggen...")
    print()

    try:
        # Reinstall from git with latest version
        subprocess.run([
            "uv", "tool", "install",
            "--reinstall",
            "--force",
            "git+https://github.com/ilkkanisula/imggen.git"
        ], check=True)

        print()
        print("✓ imggen updated successfully!")
        print()
        print("Use 'imggen --help' to see available commands")

    except subprocess.CalledProcessError as e:
        print(f"✗ Update failed: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Please ensure uv is installed.", file=sys.stderr)
        sys.exit(1)
