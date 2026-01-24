# Docker Hub Setup for Automated Deployment

## Prerequisites

You need to configure GitHub Secrets for Docker Hub authentication:

1. **Create Docker Hub Access Token:**
   - Go to https://hub.docker.com/settings/security
   - Click "New Access Token"
   - Name: `lightgroove-github-actions`
   - Permissions: Read, Write, Delete
   - Copy the generated token (you won't see it again!)

2. **Add GitHub Secrets:**
   - Go to https://github.com/oliverbyte/LightGroove/settings/secrets/actions
   - Click "New repository secret"
   - Add two secrets:
     - Name: `DOCKERHUB_USERNAME`
       Value: `oliverbyte`
     - Name: `DOCKERHUB_TOKEN`
       Value: (paste the access token from step 1)

## Workflow

The GitHub Actions workflow (`.github/workflows/docker-publish.yml`) will automatically:

1. **Trigger:** When code is pushed to the `main` branch
2. **Build:** Create Docker image from `docker/Dockerfile`
3. **Tag:** Create tags:
   - `oliverbyte/lightgroove:latest` (always points to latest main)
   - `oliverbyte/lightgroove:main-<git-sha>` (specific commit)
4. **Push:** Upload to https://hub.docker.com/r/oliverbyte/lightgroove

## Using the Published Image

Once deployed, users can run LightGroove directly from Docker Hub:

```bash
# Pull and run the latest version
docker run -d \
  --name lightgroove \
  -p 5555:5555 \
  -p 6454:6454/udp \
  -v ./config:/app/config \
  oliverbyte/lightgroove:latest

# Or use docker-compose
# (update docker-compose.yml to use oliverbyte/lightgroove:latest instead of building)
```

## Manual Testing

To manually test the workflow before pushing to main:

```bash
# Trigger workflow manually from GitHub Actions tab
# Or push to a test branch and temporarily modify the workflow trigger
```

## Troubleshooting

- **Authentication failed:** Check that `DOCKERHUB_TOKEN` is valid and not expired
- **Build failed:** Check the GitHub Actions logs at https://github.com/oliverbyte/LightGroove/actions
- **Image not found:** Ensure the repository `oliverbyte/lightgroove` exists and is public on Docker Hub
