#!/bin/bash
# Script to run Jekyll website locally for preview

echo "🚀 Starting Jekyll server for local preview..."
echo ""
echo "This will start the website at: http://localhost:4000/lightgroove"
echo "Press Ctrl+C to stop the server"
echo ""

cd website

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Using Docker to run Jekyll..."
    docker run --rm \
        --volume="$PWD:/srv/jekyll" \
        --publish 4000:4000 \
        jekyll/jekyll:4.3 \
        jekyll serve --watch --force_polling --verbose
else
    echo "Docker not found. Attempting to use local Jekyll..."
    echo ""
    
    # Try bundle exec
    if command -v bundle &> /dev/null; then
        bundle exec jekyll serve --watch --livereload
    else
        echo "❌ Error: Neither Docker nor Bundle found."
        echo ""
        echo "Please install one of the following:"
        echo "  1. Docker Desktop: https://www.docker.com/products/docker-desktop"
        echo "  2. Ruby and Bundler: https://jekyllrb.com/docs/installation/"
        echo ""
        exit 1
    fi
fi
