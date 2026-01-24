---
layout: default
title: Installation - LightGroove
description: Step-by-step installation guide for LightGroove on Windows, macOS, and Linux
permalink: /installation/
---

<div class="docs-content">
  <h1>Installation Guide</h1>
  
  <p>LightGroove is easy to install on Windows, macOS, and Linux. Choose the method that best suits your needs.</p>

  <h2>Windows (Recommended)</h2>
  
  <h3>Using the Installer</h3>
  <p>The easiest way to get started on Windows:</p>
  <ol>
    <li>Download the latest <code>LightGrooveSetup.exe</code> from the <a href="https://github.com/{{ site.repository }}/releases" target="_blank" rel="noopener">Releases page</a></li>
    <li>Run the installer and follow the prompts</li>
    <li>Launch LightGroove from the Start Menu or Desktop shortcut</li>
    <li>The web UI will automatically open at <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a></li>
  </ol>
  
  <p><strong>Note:</strong> The installer is automatically built and published whenever changes are pushed to the main branch, so you always get the latest version.</p>

  <h2>macOS</h2>
  
  <h3>Using Homebrew</h3>
  <p>The recommended installation method for macOS:</p>
  <pre><code># Add the LightGroove tap
brew tap oliverbyte/lightgroove https://github.com/oliverbyte/lightgroove.git

# Install LightGroove
brew install --HEAD oliverbyte/lightgroove/lightgroove

# Run LightGroove
lightgroove</code></pre>

  <p>After running <code>lightgroove</code>, open your browser to <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a>.</p>

  <h2>Docker (All Platforms)</h2>
  
  <h3>Using Pre-built Image</h3>
  <p>The easiest way to run LightGroove with Docker:</p>
  <pre><code># Pull and run the latest version
docker run -d \
  --name lightgroove \
  -p 5555:5555 \
  -p 6454:6454/udp \
  -v ./config:/app/config \
  oliverbyte/lightgroove:latest</code></pre>

  <p>Then open <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a> in your browser.</p>

  <h3>Using Docker Compose</h3>
  <p>For easier management and configuration:</p>
  <pre><code># Clone the repository
git clone https://github.com/{{ site.repository }}.git
cd lightgroove/docker

# Start LightGroove
docker compose up -d

# View logs
docker compose logs -f

# Stop LightGroove
docker compose down</code></pre>

  <h3>Benefits of Docker</h3>
  <ul>
    <li><strong>No Python installation required</strong> - Everything runs in a container</li>
    <li><strong>Isolated environment</strong> - No conflicts with other software</li>
    <li><strong>Easy updates</strong> - Pull latest image with <code>docker pull oliverbyte/lightgroove:latest</code></li>
    <li><strong>Cross-platform</strong> - Works identically on Windows, macOS, and Linux</li>
    <li><strong>Automatic health checks</strong> - Container monitors application health</li>
    <li><strong>Persistent configuration</strong> - Config files stored outside container</li>
  </ul>

  <p>For detailed Docker deployment instructions, see <a href="https://github.com/{{ site.repository }}/blob/main/docker/DOCKER.md" target="_blank" rel="noopener">docker/DOCKER.md</a>.</p>

  <h2>Linux</h2>
  
  <h3>From Source</h3>
  <p>The recommended method for Linux users:</p>
  <pre><code># Clone the repository
git clone https://github.com/{{ site.repository }}.git
cd lightgroove

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run LightGroove
python main.py</code></pre>

  <p>Then open <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a> in your browser.</p>

  <h2>From Source (All Platforms)</h2>
  
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.9 or higher</li>
    <li>pip (Python package installer)</li>
    <li>Git (for cloning the repository)</li>
    <li>virtualenv recommended for isolated Python environment</li>
  </ul>

  <h3>Installation Steps</h3>
  <pre><code># Clone the repository
git clone https://github.com/{{ site.repository }}.git
cd lightgroove

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run LightGroove
python main.py</code></pre>

  <h3>Dependencies</h3>
  <p>LightGroove requires the following Python packages (automatically installed via requirements.txt):</p>
  <ul>
    <li><strong>Flask</strong> - Web framework for the UI</li>
    <li><strong>stupidArtnet</strong> - ArtNet protocol implementation</li>
    <li>Additional supporting libraries as specified in requirements.txt</li>
  </ul>

  <h2>First Run</h2>
  
  <p>After installation, LightGroove will:</p>
  <ol>
    <li>Start the web server on port 5555</li>
    <li>Load configuration files from the <code>config/</code> directory</li>
    <li>Begin sending ArtNet data to configured nodes</li>
    <li>Open the web UI in your default browser (or manually navigate to <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a>)</li>
  </ol>

  <h2>Configuration</h2>
  
  <p>Before using LightGroove with your lighting setup, you'll need to configure:</p>
  
  <h3>1. Fixtures</h3>
  <p>Define your fixture profiles in <code>config/fixtures.json</code> or use the provided examples. Each fixture needs:</p>
  <ul>
    <li>Channel definitions (dimmer, red, green, blue, white, etc.)</li>
    <li>Channel order and offsets</li>
  </ul>

  <h3>2. Patch</h3>
  <p>Configure which fixtures are patched to which universes and DMX addresses in <code>config/patch.json</code>.</p>

  <h3>3. ArtNet Nodes</h3>
  <p>Set up your ArtNet output nodes using the <strong>Config tab</strong> in the web UI:</p>
  <ul>
    <li>Add ArtNet node IP addresses</li>
    <li>Configure universe mapping (DMX universe → ArtNet universe)</li>
    <li>Set target universes for each node</li>
  </ul>

  <h3>4. Colors (Optional)</h3>
  <p>Customize color definitions in the <strong>Config tab</strong> or edit <code>config/colors.json</code> directly. Define RGBW values (0.0-1.0 range) for each color.</p>

  <h2>Network Setup</h2>
  
  <h3>For ArtNet Output</h3>
  <p>Ensure your computer and ArtNet nodes are on the same network:</p>
  <ol>
    <li>Connect your computer and ArtNet interface to the same network switch or router</li>
    <li>Configure your ArtNet node's IP address (check the device documentation)</li>
    <li>Add the ArtNet node in LightGroove's Config tab with the correct IP address</li>
    <li>Verify connectivity by checking DMX output on your fixtures</li>
  </ol>

  <h3>Firewall Configuration</h3>
  <p>If you encounter issues:</p>
  <ul>
    <li>Allow LightGroove through your firewall</li>
    <li>Ensure UDP traffic is allowed on your network</li>
    <li>ArtNet uses UDP port 6454 by default</li>
  </ul>

  <h2>Updating</h2>
  
  <h3>Windows Installer</h3>
  <p>Download and run the latest installer from the <a href="https://github.com/{{ site.repository }}/releases" target="_blank" rel="noopener">Releases page</a>. It will update your installation automatically.</p>

  <h3>Homebrew (macOS)</h3>
  <pre><code>brew upgrade lightgroove</code></pre>

  <h3>Docker</h3>
  <pre><code>docker pull oliverbyte/lightgroove:latest
docker compose restart  # if using docker-compose</code></pre>

  <h3>From Source</h3>
  <pre><code>cd lightgroove
git pull
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt --upgrade</code></pre>

  <h2>Troubleshooting</h2>
  
  <h3>Port Already in Use</h3>
  <p>If port 5555 is already in use, you can modify the port in <code>main.py</code> or stop the other application using the port.</p>

  <h3>No DMX Output</h3>
  <p>Check the following:</p>
  <ul>
    <li>ArtNet node IP address is correct in Config tab</li>
    <li>ArtNet node is powered on and connected to the network</li>
    <li>Universe mapping is configured correctly</li>
    <li>Fixtures are patched in <code>config/patch.json</code></li>
    <li>Master fader is not at 0%</li>
  </ul>

  <h3>Web UI Not Loading</h3>
  <p>Try the following:</p>
  <ul>
    <li>Clear your browser cache</li>
    <li>Try a different browser</li>
    <li>Check if the server is running (check terminal output)</li>
    <li>Verify you're accessing <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a></li>
  </ul>

  <h2>Getting Help</h2>
  
  <p>If you encounter issues:</p>
  <ul>
    <li>Check the <a href="https://github.com/{{ site.repository }}/issues" target="_blank" rel="noopener">GitHub Issues</a> for known problems</li>
    <li>Join the <a href="https://github.com/{{ site.repository }}/discussions" target="_blank" rel="noopener">Discussions</a> to ask questions</li>
    <li>Review the <a href="{{ '/docs' | relative_url }}">Documentation</a> for configuration details</li>
    <li>Open a new issue with details about your problem</li>
  </ul>
</div>
