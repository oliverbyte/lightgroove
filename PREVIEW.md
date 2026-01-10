# Website Preview Options

This directory contains the Jekyll-based website for LightGroove.

## Quick Preview

### Using Docker (Recommended - Full Jekyll Processing)
```bash
./run_website.sh
```
Then visit: http://localhost:4000/lightgroove/

### Using Python (Quick Preview - No Jekyll Processing)
```bash
python3 preview_website.py
```
Then visit: http://localhost:4000/lightgroove/

**Note:** The Python preview serves static files only. Markdown and Liquid templates are NOT processed. For full Jekyll rendering, use Docker or Ruby/Jekyll.

### Using Ruby/Jekyll (If You Have Ruby Installed)
```bash
cd website
bundle install --path vendor/bundle
bundle exec jekyll serve
```
Then visit: http://localhost:4000/lightgroove/

## What Gets Deployed

When you push to the `main` branch, GitHub Actions automatically:
1. Builds the Jekyll site with all Markdown and Liquid processing
2. Generates the final HTML pages
3. Deploys to GitHub Pages

The screenshot script only runs when pushing to `main`, not other branches.

## Files

- `run_website.sh` - Docker-based Jekyll server (recommended)
- `preview_website.py` - Simple Python preview server (quick but limited)
- `website/` - All Jekyll source files
