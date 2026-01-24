---
layout: default
title: Documentation - LightGroove
description: Complete documentation for LightGroove DMX lighting controller
permalink: /docs/
---

<div class="docs-content">
  <h1>Documentation</h1>
  
  <p>Complete guide to using and configuring LightGroove.</p>

  <h2>Quick Start</h2>
  
  <ol>
    <li><a href="{{ '/installation' | relative_url }}">Install LightGroove</a> for your platform</li>
    <li>Launch the application - the web UI will open at <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a></li>
    <li>Configure your ArtNet nodes in the <strong>Config tab</strong></li>
    <li>Start controlling your lights from the <strong>Faders</strong> or <strong>Colors</strong> tabs</li>
  </ol>

  <h2>User Interface Guide</h2>

  <h3>Globals Tab</h3>
  <p>Master controls that affect all fixtures:</p>
  <ul>
    <li><strong>Master</strong> (0-100%): Scales all DMX output. Use this as a global brightness control without touching individual faders.</li>
    <li><strong>FX BPM</strong> (1-480): Controls the speed of color effects in beats per minute.</li>
    <li><strong>FX Fade</strong> (0-100%): Smoothness of color transitions as a percentage of the beat interval. 0% = instant, 100% = smooth fade over entire beat.</li>
  </ul>

  <h3>Faders Tab</h3>
  <p>Individual fixture control:</p>
  <ul>
    <li>Each fixture is displayed as a card with its name and channels</li>
    <li>Vertical faders control each channel (Dimmer, R, G, B, W, etc.)</li>
    <li>DMX values (0-255) are displayed in real-time below each fader</li>
    <li>Changes are sent immediately to the DMX output</li>
  </ul>

  <h3>Colors Tab</h3>
  
  <h4>Static Colors</h4>
  <p>Click any color button to set all fixtures to that color:</p>
  <ul>
    <li>Red, Green, Blue - Primary colors</li>
    <li>Cyan, Magenta, Yellow - Secondary colors</li>
    <li>White, Orange, Purple - Additional colors</li>
    <li>Black - Turns all color channels off</li>
  </ul>
  <p>Colors are defined in <code>config/colors.json</code> and can be edited in the Config tab.</p>

  <h4>Color FX</h4>
  <p>Dynamic effects that run on the server:</p>
  <ul>
    <li><strong>Random 1</strong>: All fixtures show the same random color, changing at BPM speed</li>
    <li><strong>Random 2</strong>: Each fixture gets a different random color every beat</li>
    <li><strong>Random 3</strong>: Even/odd fixtures alternate with black (strobe effect)</li>
    <li><strong>Random 4</strong>: Chaser - one fixture at a time in sequence</li>
  </ul>
  <p>All effects respect the FX BPM and FX Fade settings from the Globals tab.</p>

  <h3>Config Tab</h3>
  <p>Web-based configuration editor:</p>
  
  <h4>ArtNet Nodes</h4>
  <ul>
    <li>Add new nodes with IP address and universe number</li>
    <li>Edit existing nodes</li>
    <li>Delete nodes you no longer need</li>
  </ul>

  <h4>Universe Mapping</h4>
  <ul>
    <li>Map DMX universes to ArtNet nodes and universes</li>
    <li>Example: DMX Universe 1 → Node IP 192.168.1.100, ArtNet Universe 0</li>
  </ul>

  <h4>Colors</h4>
  <ul>
    <li>Edit RGBW values (0.0-1.0) for each color with sliders</li>
    <li>Live preview shows the color as you edit</li>
    <li>Add new colors or remove existing ones</li>
  </ul>

  <h4>Global Settings</h4>
  <ul>
    <li>Default output mode</li>
    <li>Frames per second (FPS)</li>
  </ul>

  <p><strong>Note:</strong> All changes are saved immediately and the server reloads automatically.</p>

  <h2>Configuration Files</h2>

  <h3>fixtures.json</h3>
  <p>Defines fixture types and their channel layouts:</p>
  <pre><code>{
  "PAR_RGBW": {
    "channels": {
      "dimmer": 0,
      "red": 1,
      "green": 2,
      "blue": 3,
      "white": 4
    }
  }
}</code></pre>

  <h3>patch.json</h3>
  <p>Maps fixtures to DMX universes and addresses:</p>
  <pre><code>{
  "1": [
    {
      "fixture": "PAR_RGBW",
      "address": 1,
      "name": "Front Left"
    },
    {
      "fixture": "PAR_RGBW",
      "address": 6,
      "name": "Front Right"
    }
  ]
}</code></pre>

  <h3>artnet.json</h3>
  <p>Configures ArtNet output nodes and universe mapping:</p>
  <pre><code>{
  "nodes": [
    {
      "ip": "192.168.1.100",
      "universe": 0
    }
  ],
  "universe_mapping": {
    "1": {
      "node_ip": "192.168.1.100",
      "artnet_universe": 0
    }
  }
}</code></pre>

  <h3>colors.json</h3>
  <p>Defines RGBW color values (0.0-1.0 range):</p>
  <pre><code>{
  "red": {"r": 1.0, "g": 0.0, "b": 0.0, "w": 0.0},
  "green": {"r": 0.0, "g": 1.0, "b": 0.0, "w": 0.0},
  "blue": {"r": 0.0, "g": 0.0, "b": 1.0, "w": 0.0},
  "white": {"r": 0.0, "g": 0.0, "b": 0.0, "w": 1.0}
}</code></pre>

  <h2>DMX and ArtNet</h2>

  <h3>What is DMX?</h3>
  <p>DMX512 is the standard lighting control protocol. It sends data to fixtures telling them what to do (brightness, color, etc.). Each DMX universe can control up to 512 channels.</p>

  <h3>What is ArtNet?</h3>
  <p>ArtNet is a protocol for sending DMX data over Ethernet networks. It allows you to control DMX fixtures using network equipment instead of traditional DMX cables.</p>

  <h3>How LightGroove Uses ArtNet</h3>
  <ol>
    <li>LightGroove generates DMX values based on your fader positions and color settings</li>
    <li>These values are packaged into ArtNet packets</li>
    <li>Packets are sent over your network to ArtNet nodes</li>
    <li>ArtNet nodes convert the network data back to DMX signals</li>
    <li>DMX signals control your lighting fixtures</li>
  </ol>

  <h2>Hardware Setup</h2>

  <h3>Required Equipment</h3>
  <ul>
    <li><strong>Computer</strong> running LightGroove (Windows, macOS, or Linux)</li>
    <li><strong>Network</strong> (router/switch) to connect computer and ArtNet nodes</li>
    <li><strong>ArtNet Node</strong> (e.g., Enttec ODE, DMXking eDMX1, etc.) to convert ArtNet to DMX</li>
    <li><strong>DMX Fixtures</strong> (lights) with DMX input</li>
    <li><strong>DMX Cables</strong> to connect fixtures (standard 5-pin XLR or 3-pin XLR)</li>
  </ul>

  <h3>Connection Diagram</h3>
  <pre><code>Computer (LightGroove)
    |
    | Ethernet
    |
Network Switch/Router
    |
    | Ethernet
    |
ArtNet Node
    |
    | DMX Cable
    |
Lighting Fixtures (daisy-chained)</code></pre>

  <h3>Network Configuration</h3>
  <ol>
    <li>Connect your computer and ArtNet node to the same network</li>
    <li>Set the ArtNet node to a static IP or note its DHCP-assigned address</li>
    <li>Configure the ArtNet node's universe in its settings</li>
    <li>Add the node's IP address in LightGroove's Config tab</li>
  </ol>

  <h2>Advanced Usage</h2>

  <h3>Multiple Universes</h3>
  <p>You can use multiple DMX universes for large setups:</p>
  <ol>
    <li>Add fixtures to different universes in <code>patch.json</code></li>
    <li>Configure universe mapping in the Config tab</li>
    <li>Each universe can go to a different ArtNet node or different universe on the same node</li>
  </ol>

  <h3>Custom Fixture Profiles</h3>
  <p>Create profiles for any fixture type:</p>
  <ol>
    <li>Determine the fixture's channel layout from its manual</li>
    <li>Add a new fixture type in <code>fixtures.json</code></li>
    <li>Define each channel and its offset from the start address</li>
    <li>Use the new fixture type in <code>patch.json</code></li>
  </ol>

  <h3>HTTP API</h3>
  <p>LightGroove exposes a REST API for integration:</p>
  <ul>
    <li><code>GET /api/state</code> - Get current state</li>
    <li><code>POST /api/master</code> - Set master level</li>
    <li><code>POST /api/color</code> - Set color</li>
    <li><code>POST /api/fader</code> - Control individual channels</li>
  </ul>
  <p>See the code in <code>src/http_api.py</code> for full API documentation.</p>

  <h2>Performance Tips</h2>
  <ul>
    <li>Use wired Ethernet for ArtNet nodes when possible (more reliable than WiFi)</li>
    <li>Keep ArtNet nodes on the same network segment as the computer</li>
    <li>Adjust FPS in config if you experience network congestion</li>
    <li>Use quality DMX cables and terminators for long cable runs</li>
  </ul>

  <h2>Development</h2>
  <p>For development setup, architecture details, and contribution guidelines, see <a href="https://github.com/{{ site.repository }}/blob/main/DEVELOPMENT.md" target="_blank" rel="noopener">DEVELOPMENT.md</a> on GitHub.</p>

  <h2>Contributing</h2>
  <p>Contributions are welcome! Please:</p>
  <ol>
    <li>Fork the repository</li>
    <li>Create a feature branch</li>
    <li>Make your changes</li>
    <li>Submit a pull request</li>
  </ol>
  <p>See the <a href="https://github.com/{{ site.repository }}/issues" target="_blank" rel="noopener">Issues page</a> for ideas or report bugs.</p>

  <h2>License</h2>
  <p>LightGroove is released under the GNU Affero General Public License v3.0 (AGPL-3.0). See <a href="https://github.com/{{ site.repository }}/blob/main/LICENSE" target="_blank" rel="noopener">LICENSE</a> for details.</p>
</div>
