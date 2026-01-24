# LightGroove Docker Deployment

Run LightGroove DMX controller in a Docker container for easy deployment and isolation.

## Prerequisites

### Docker Installation

**macOS:**
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or use Homebrew:
brew install --cask docker
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Windows:**
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

### Docker Compose

Modern Docker installations (Docker Desktop, Docker Engine 20.10+) include Docker Compose as `docker compose` (no hyphen).

If you have an older installation, you may need to install docker-compose separately:
```bash
# macOS
brew install docker-compose

# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Quick Start

### Option 1: Using Pre-built Image from Docker Hub (Easiest)

**Step 1: Create config directory and get default configs**
```bash
# Create a directory for LightGroove
mkdir -p ~/lightgroove
cd ~/lightgroove

# Clone just the config files from the repository
git clone --depth 1 --filter=blob:none --sparse https://github.com/oliverbyte/lightgroove.git temp
cd temp
git sparse-checkout set config
mv config ..
cd ..
rm -rf temp

# Or download the config files manually from:
# https://github.com/oliverbyte/lightgroove/tree/main/config
```

**Step 2: Run the container**
```bash
# Run LightGroove with your config directory
docker run -d \
  --name lightgroove \
  -p 5555:5555 \
  -p 6454:6454/udp \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  oliverbyte/lightgroove:latest

# View logs
docker logs -f lightgroove

# Stop container
docker stop lightgroove

# Remove container
docker rm lightgroove
```

**Step 3: Access the UI**
Open `http://localhost:5555` in your browser.

**Step 4: Edit configurations**
All configuration files in your `~/lightgroove/config/` directory are now persistent and can be edited:
- `artnet.json` - ArtNet output nodes
- `fixtures.json` - Fixture definitions  
- `patch.json` - Fixture patching
- `colors.json` - Color definitions
- `color_state.json` - Color FX state (auto-saved)
- `move_state.json` - Move FX state (auto-saved)

Changes to configuration files are immediately reflected in the running container.

### Option 2: Using Docker Compose (Recommended for Development)

**Modern Docker (v20.10+):**
```bash
# Clone the repository
git clone https://github.com/oliverbyte/lightgroove.git
cd lightgroove/docker

# Build and start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

**Legacy docker-compose:**
```bash
# Navigate to docker directory
cd docker

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The web UI will be available at `http://localhost:5555`

### Option 3: Building from Source

```bash
# Build the image from project root
docker build -f docker/Dockerfile -t lightgroove .

# Run the container
docker run -d \
  --name lightgroove \
  --network host \
  -v $(pwd)/config:/app/config \
  lightgroove

# View logs
docker logs -f lightgroove

# Stop the container
docker stop lightgroove
docker rm lightgroove
```

## Network Configuration

### Host Network Mode (Recommended for ArtNet)

For ArtNet to work properly with broadcast/multicast, use host network mode:

```yaml
network_mode: host
```

This allows the container to send ArtNet packets directly to your network.

### Bridge Network Mode

If you prefer network isolation, use bridge mode and map ports:

```yaml
ports:
  - "5555:5555"
networks:
  - lightgroove-network
```

**Note:** Bridge mode may require additional configuration for ArtNet multicast/broadcast to work properly.

## Configuration Persistence

The `config/` directory is mounted as a volume to persist your settings:

- `config/fixtures.json` - Fixture definitions
- `config/patch.json` - Patched fixtures
- `config/artnet.json` - ArtNet nodes and universe mapping
- `config/colors.json` - Color definitions
- `config/color_state.json` - Color FX state
- `config/move_state.json` - Move FX state

Edit these files directly or use the Config tab in the web UI.

## Environment Variables

- `LIGHTGROOVE_HTTP_PORT` - HTTP server port (default: 5555)

Example:
```bash
docker run -d \
  --name lightgroove \
  --network host \
  -e LIGHTGROOVE_HTTP_PORT=8080 \
  -v $(pwd)/config:/app/config \
  lightgroove
```

## Health Check

The container includes a health check that verifies the API is responding:

```bash
# Check container health
docker ps
# Look for "healthy" status

# Manual health check
docker exec lightgroove curl -f http://localhost:5555/api/grandmaster
```

## Building from Scratch

```bash
# Clone the repository
git clone https://github.com/oliverbyte/lightgroove.git
cd lightgroove

# Build the image
docker build -f docker/Dockerfile -t lightgroove:latest .

# Run with docker-compose
cd docker
docker-compose up -d
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs lightgroove
```

### ArtNet Not Working

1. Ensure you're using host network mode: `network_mode: host`
2. Check your ArtNet node configuration in `config/artnet.json`
3. Verify your ArtNet nodes are on the same network as the Docker host

### Configuration Not Persisting

Ensure the volume is mounted correctly:
```bash
docker inspect lightgroove | grep -A 5 Mounts
```

Should show: `"Source": "/path/to/your/config"`

## Updating

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart (modern Docker)
cd docker
docker compose down
docker compose build
docker compose up -d

# Or with legacy docker-compose
cd docker
docker-compose down
docker-compose build
docker-compose up -d
```

## Accessing from Other Devices

The web UI can be accessed from any device on your network:

```
http://<docker-host-ip>:5555
```

Replace `<docker-host-ip>` with your Docker host's IP address.

## Security Considerations

- The container runs as root by default (required for some network operations)
- Expose port 5555 only on trusted networks
- Consider using a reverse proxy (nginx, traefik) for HTTPS and authentication

## License

MIT License - See main README.md for details
