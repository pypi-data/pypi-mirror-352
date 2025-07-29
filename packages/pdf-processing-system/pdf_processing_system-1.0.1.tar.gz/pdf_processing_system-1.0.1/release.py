#!/usr/bin/env python3
"""
Release script for PDF Processing System
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean existing build directories."""
    print("🧹 Cleaning build directories...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    
    for pattern in dirs_to_clean:
        if "*" in pattern:
            # Use glob for wildcard patterns
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    subprocess.run(["rmdir", "/s", "/q", path], shell=True)
        else:
            if os.path.exists(pattern):
                subprocess.run(["rmdir", "/s", "/q", pattern], shell=True)

def main():
    """Main release process."""
    print("📦 PDF Processing System - Release Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("❌ Error: setup.py not found. Please run from the project root.")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Install/upgrade build tools
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "build", "twine"], 
                      "Installing/upgrading build tools"):
        sys.exit(1)
    
    # Build the package
    if not run_command([sys.executable, "-m", "build"], "Building package"):
        sys.exit(1)
    
    # Check the package
    if not run_command([sys.executable, "-m", "twine", "check", "dist/*"], 
                      "Checking package"):
        sys.exit(1)
    
    print("\n✅ Package built successfully!")
    print("\n📁 Generated files:")
    
    # List generated files
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            file_path = os.path.join("dist", file)
            file_size = os.path.getsize(file_path)
            print(f"  📄 {file} ({file_size:,} bytes)")
    
    print("\n🚀 Next steps:")
    print("1. Test the package locally:")
    print("   pip install dist/pdf_processing_system-1.0.0-py3-none-any.whl")
    print("\n2. Upload to PyPI (when ready):")
    print("   python -m twine upload dist/*")
    print("\n3. Create a Git tag:")
    print("   git tag -a v1.0.0 -m 'Release v1.0.0'")
    print("   git push origin v1.0.0")

if __name__ == "__main__":
    main()
