# Git and GitHub Workflow Instructions

## Automated Website Deployment

The LightGroove project includes an automated Jekyll website that deploys to GitHub Pages whenever changes are pushed to the `main` branch.

### Workflow Details

**Trigger**: Automatic deployment on push to `main` branch
**Platform**: GitHub Pages via GitHub Actions
**Technology**: Jekyll static site generator
**URL**: Will be available at `https://oliverbyte.github.io/lightgroove` once enabled

### Setup Requirements (One-Time)

After merging the `feature/website` branch to `main`, you need to enable GitHub Pages in the repository settings:

1. Go to repository Settings → Pages
2. Under "Build and deployment":
   - Source: Select "GitHub Actions"
3. The workflow will automatically run on the next push to `main`

### What Happens on Push to Main

When code is pushed to the `main` branch, the GitHub Actions workflow automatically:

1. Checks out the code
2. Sets up Ruby and Jekyll environment
3. Installs dependencies from Gemfile
4. Builds the Jekyll website with all pages
5. Generates sitemap and SEO tags
6. Deploys to GitHub Pages
7. Website becomes available at the GitHub Pages URL

### Website Content

The website automatically includes:
- **Homepage** (`index.md`) - Hero section, features overview, screenshots, quick install
- **Features Page** (`_pages/features.md`) - Detailed feature descriptions
- **Installation Page** (`_pages/installation.md`) - Step-by-step installation for all platforms
- **Documentation Page** (`_pages/docs.md`) - Complete user guide and technical docs
- **SEO Optimization** - Meta tags, sitemap.xml, robots.txt, Open Graph tags

### Files That Control Website

- `_config.yml` - Jekyll configuration, site metadata, SEO settings
- `Gemfile` - Ruby gem dependencies
- `_layouts/default.html` - Main page layout template
- `_pages/*.md` - Content pages
- `index.md` - Homepage content
- `assets/css/style.css` - Website styling
- `assets/js/main.js` - Interactive features
- `.github/workflows/jekyll-gh-pages.yml` - Deployment automation

### Local Testing

To preview the website locally before pushing:

```bash
# Install Ruby dependencies (first time only)
bundle install

# Serve website locally
bundle exec jekyll serve

# Visit http://localhost:4000/lightgroove in your browser
```

### Updating the Website

To update website content:

1. Edit the relevant Markdown files (`index.md`, `_pages/*.md`)
2. Commit and push to `main` branch
3. GitHub Actions will automatically rebuild and deploy
4. Changes appear on the live site within 2-3 minutes

### SEO Features

The website is optimized for search engines:
- Semantic HTML structure
- Meta descriptions on all pages
- Open Graph tags for social media
- Twitter Card tags
- Sitemap.xml (auto-generated)
- robots.txt for crawler guidance
- Fast loading with minimal dependencies
- Mobile-responsive design

### Monitoring Deployments

To check deployment status:
1. Go to repository → Actions tab
2. Look for "Deploy Jekyll Website to GitHub Pages" workflow
3. Click on any run to see build logs
4. Green checkmark = successful deployment
5. Red X = failed deployment (check logs for errors)

### Important Notes

- **Automatic Only**: Website deploys ONLY on push to `main`, not other branches
- **No Manual Action**: No need to manually trigger deployments
- **Build Time**: Takes 2-3 minutes from push to live site
- **Cache**: Browser may cache old version, do hard refresh (Cmd+Shift+R / Ctrl+F5)
- **Screenshots**: Images in `img/` folder are automatically included
- **Updates**: Any change to `.md` files, layouts, or assets triggers rebuild

### Branch Workflow

```
feature/website (current) → merge to → main → auto deploy to GitHub Pages
```

After merging this branch to main, all future pushes to main will automatically update the website.

### Troubleshooting

**Website not updating?**
- Check Actions tab for failed deployments
- Verify GitHub Pages is enabled in Settings
- Clear browser cache

**Build failing?**
- Check workflow logs in Actions tab
- Verify Gemfile dependencies are correct
- Ensure all Markdown files have valid front matter

**404 errors on pages?**
- Check `permalink:` in page front matter
- Verify `baseurl` in `_config.yml` is correct
- Ensure files are in correct directories

### Contact for Issues

If deployment fails or website has issues, check:
1. GitHub Actions logs for error messages
2. Jekyll documentation at https://jekyllrb.com/docs/
3. GitHub Pages documentation at https://docs.github.com/pages
