# LightGroove Development Tools

## Automated Screenshot Updates

This project includes a Git pre-push hook that automatically updates UI screenshots before pushing to remote.

### Setup

The hook is already installed at `.git/hooks/pre-push` (not tracked in git).

To set up on a new clone:

```bash
# Copy the pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook to automatically update screenshots before pushing

echo "🔍 Checking for UI changes..."

# Run screenshot script
python3.9 take_screenshots.py

# Check if screenshots changed
if git diff --quiet img/screenshot_faders.png img/screenshot_colors.png; then
    echo "✓ Screenshots are up to date"
else
    echo "📸 Screenshots updated, adding to commit..."
    git add img/screenshot_faders.png img/screenshot_colors.png
    git commit --amend --no-edit
    echo "✓ Screenshots committed"
fi

exit 0
EOF

# Make it executable
chmod +x .git/hooks/pre-push
```

### Manual Screenshot Update

To manually update screenshots:

```bash
python3.9 take_screenshots.py
```

Requires: `pip install playwright && playwright install chromium`
