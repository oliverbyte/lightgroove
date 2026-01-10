# Jekyll GitHub Pages Website

This directory contains the Jekyll-based website for LightGroove that automatically deploys to GitHub Pages when changes are pushed to the main branch.

## Website Structure

- `_config.yml` - Jekyll configuration
- `_layouts/` - Page layouts
- `_pages/` - Content pages (features, installation, docs)
- `assets/` - CSS, JavaScript, and other static assets
- `index.md` - Homepage
- `Gemfile` - Ruby dependencies
- `.github/workflows/jekyll-gh-pages.yml` - GitHub Actions deployment workflow

## Local Development

To run the website locally:

### Option 1: Using Docker (Recommended)
```bash
# From the project root
./run_website.sh

# Or manually:
cd website
docker run --rm \
  --volume="$PWD:/srv/jekyll" \
  --publish 4000:4000 \
  jekyll/jekyll:4.3 \
  jekyll serve --watch --force_polling
```

### Option 2: Using Ruby/Jekyll
```bash
cd website

# Install dependencies (first time only)
bundle install --path vendor/bundle

# Serve the site locally
bundle exec jekyll serve

# Visit http://localhost:4000/lightgroove
```

### Option 3: Simple Preview (No Jekyll Processing)
```bash
# From the project root
python3 preview_website.py

# Visit http://localhost:4000/lightgroove/
# Note: This won't process Markdown or Liquid templates
```

## Deployment

The website automatically deploys to GitHub Pages when changes are pushed to the `main` branch via GitHub Actions.

## SEO Optimization

The site includes:
- SEO-optimized meta tags via `jekyll-seo-tag`
- Automatic sitemap generation via `jekyll-sitemap`
- RSS feed via `jekyll-feed`
- Semantic HTML structure
- Open Graph and Twitter Card meta tags
- robots.txt for search engine crawling

## Design

The website uses:
- Modern, gradient-based design
- Responsive layout for mobile and desktop
- Clean typography with Inter font
- Smooth animations and transitions
- Accessible color contrast
- SEO-friendly structure
