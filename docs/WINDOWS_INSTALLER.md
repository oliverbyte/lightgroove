# Windows Installer Build

This directory contains configuration files for building a Windows installer for LightGroove.

## Files

- **`.github/workflows/windows-installer.yml`**: GitHub Actions workflow that automatically builds the installer when pushing to main
- **`LightGroove.spec`**: PyInstaller specification file for building the Windows executable
- **`installer_script.iss`**: Inno Setup script for creating the Windows installer

## How it works

1. On push to main branch, GitHub Actions automatically:
   - Sets up Python 3.9 on Windows
   - Installs dependencies
   - Builds executable with PyInstaller
   - Creates installer with Inno Setup
   - Uploads installer as artifact (available for 90 days)

2. The installer includes:
   - LightGroove executable
   - Configuration files
   - README

3. Installation features:
   - Desktop icon (optional)
   - Start menu entry
   - Automatic browser launch on first run

## Manual build (local)

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller LightGroove.spec

# Install Inno Setup from https://jrsoftware.org/isdl.php
# Then run:
iscc installer_script.iss
```

The installer will be created in `Output/LightGrooveSetup.exe`.
