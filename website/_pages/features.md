---
layout: default
title: Features - LightGroove
description: Explore all the powerful features of LightGroove DMX lighting controller
permalink: /features/
---

<div class="docs-content">
  <h1>Features</h1>
  
  <h2>DMX / ArtNet Output</h2>
  <ul>
    <li><strong>ArtNet by Default</strong> - Sends lighting data via ArtNet protocol to any compatible network node or monitor</li>
    <li><strong>Universal Compatibility</strong> - Works with any ArtNet-to-DMX interface like Enttec ODE, DMXking, or similar devices</li>
    <li><strong>Universe Mapping</strong> - Flexible mapping in <code>config/artnet.json</code> (e.g., DMX universe 1 → ArtNet universe 0)</li>
    <li><strong>Multiple Nodes</strong> - Support for multiple ArtNet nodes on different network addresses</li>
  </ul>

  <h2>Web-Based User Interface</h2>
  
  <h3>Globals Tab</h3>
  <img src="{{ '/img/screenshot_globals.png' | relative_url }}" alt="Globals Interface">
  <ul>
    <li><strong>Master Fader</strong> - Global intensity control (0-100%) that scales all DMX output in real-time without changing individual fader positions</li>
    <li><strong>FX BPM Control</strong> - Set the speed of color effects from 1-480 beats per minute for perfect timing</li>
    <li><strong>FX Fade</strong> - Adjust smooth color transitions from instant (0%) to full beat interval (100%)</li>
  </ul>

  <h3>Faders Tab</h3>
  <img src="{{ '/img/screenshot_faders.png' | relative_url }}" alt="Faders Interface">
  <ul>
    <li><strong>Compact Fixture Cards</strong> - Clean, organized layout showing each fixture with its channels</li>
    <li><strong>Vertical Faders</strong> - Intuitive faders arranged in channel order for precise control</li>
    <li><strong>Real-Time Values</strong> - Live DMX values (0-255) update as you move faders</li>
    <li><strong>Responsive Layout</strong> - Automatically adapts to your screen width for optimal viewing on any device</li>
  </ul>

  <h3>Colors Tab</h3>
  <img src="{{ '/img/screenshot_colors.png' | relative_url }}" alt="Colors Interface">
  
  <h4>Static Colors</h4>
  <p>10 preset color buttons with instant activation:</p>
  <ul>
    <li>Red, Green, Blue, Cyan, Magenta, Yellow</li>
    <li>White, Orange, Purple, Black</li>
    <li>Colors are defined in <code>config/colors.json</code> with RGBW values (0.0-1.0 range)</li>
    <li>Buttons automatically display the actual color from definitions</li>
  </ul>

  <h4>Color FX (Server-Side Effects)</h4>
  <p>Dynamic effects that run independently on the server:</p>
  <ul>
    <li><strong>Random 1</strong> - All fixtures display the same color, cycling through random colors at BPM speed</li>
    <li><strong>Random 2</strong> - Each fixture gets a different random color, changing at each beat for a dynamic look</li>
    <li><strong>Random 3</strong> - Alternates between even/odd patches with black, creating a strobe-like effect</li>
    <li><strong>Random 4</strong> - Chaser effect lighting one fixture at a time in sequence with random colors</li>
    <li>All effects support smooth fade transitions based on FX Fade setting</li>
    <li>Active effect buttons highlight to show what's running</li>
    <li>Multi-color highlighting for Random 2/3/4 shows all active colors</li>
  </ul>

  <h3>Config Tab</h3>
  <img src="{{ '/img/screenshot_config.png' | relative_url }}" alt="Config Interface">
  <ul>
    <li><strong>ArtNet Nodes</strong> - Add, edit, and delete ArtNet output nodes with IP addresses and universe numbers</li>
    <li><strong>Universe Mapping</strong> - Configure which DMX universe maps to which ArtNet node and universe</li>
    <li><strong>Colors Editor</strong> - Edit RGBW color definitions (0-1 range) with live preview, add/remove colors as needed</li>
    <li><strong>Global Settings</strong> - Configure default output mode and frames per second</li>
    <li><strong>Auto-Reload</strong> - Changes are saved immediately and the server reloads automatically without restart</li>
    <li><strong>Live Preview</strong> - See color changes in real-time as you adjust RGBW sliders</li>
  </ul>

  <h2>Configuration System</h2>
  <p>All settings can be managed through the web UI or by editing JSON files directly:</p>
  <ul>
    <li><code>config/fixtures.json</code> - Fixture profiles with channel definitions (dimmer, red, green, blue, white, etc.)</li>
    <li><code>config/patch.json</code> - Patched fixtures per universe with DMX start addresses</li>
    <li><code>config/artnet.json</code> - ArtNet target nodes and universe mapping configuration</li>
    <li><code>config/colors.json</code> - Color definitions for static colors and FX (RGBW values 0.0-1.0)</li>
  </ul>

  <h2>Technical Features</h2>
  <ul>
    <li><strong>Real-Time Performance</strong> - Low-latency DMX output with configurable frame rate</li>
    <li><strong>Multiple Universes</strong> - Support for multiple DMX universes through ArtNet</li>
    <li><strong>Flexible Fixture Profiles</strong> - Define any fixture type with custom channel layouts</li>
    <li><strong>Cross-Platform</strong> - Works on Windows, macOS, and Linux</li>
    <li><strong>No External Dependencies</strong> - Self-contained web server, no separate software needed</li>
    <li><strong>RESTful API</strong> - HTTP API for integration with other software</li>
    <li><strong>Auto-Discovery</strong> - Web UI automatically opens at http://localhost:5555 on startup</li>
  </ul>

  <h2>Use Cases</h2>
  <ul>
    <li>Small to medium live events and performances</li>
    <li>Architectural lighting installations</li>
    <li>DJ setups and mobile lighting</li>
    <li>Theater productions</li>
    <li>House parties and events</li>
    <li>Development and testing of lighting fixtures</li>
    <li>Educational purposes and lighting experimentation</li>
  </ul>
</div>
