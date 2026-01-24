---
layout: default
title: FAQ - LightGroove
description: Frequently asked questions about LightGroove DMX lighting controller
permalink: /faq/
---

<div class="docs-content">
  <h1>Frequently Asked Questions</h1>
  
  <p>Find answers to common questions about LightGroove installation, configuration, and usage.</p>

  <h2>General Questions</h2>

  <h3>What is LightGroove?</h3>
  <p>LightGroove is a free, open-source DMX lighting controller with a web-based user interface. It allows you to control DMX lighting fixtures through an intuitive browser interface, sending DMX data via the ArtNet protocol over your network.</p>

  <h3>Is LightGroove free?</h3>
  <p>Yes! LightGroove is completely free and open-source, released under the AGPL-3.0 License. You can use it for personal or commercial projects without any cost.</p>

  <h3>What platforms does LightGroove support?</h3>
  <p>LightGroove runs on Windows, macOS, and Linux. Windows users can use the installer, macOS users can install via Homebrew, and all platforms can run from Python source code.</p>

  <h3>Do I need programming experience to use LightGroove?</h3>
  <p>No programming experience is required for basic usage. The web interface is designed to be user-friendly. However, Python knowledge is helpful if you want to customize fixtures or contribute to development.</p>

  <h2>Installation & Setup</h2>

  <h3>What hardware do I need?</h3>
  <p>At minimum, you need:</p>
  <ul>
    <li>A computer running Windows, macOS, or Linux</li>
    <li>An ArtNet-to-DMX interface (e.g., Enttec ODE, DMXking eDMX1)</li>
    <li>DMX lighting fixtures</li>
    <li>Network equipment (router/switch) to connect everything</li>
    <li>DMX cables to connect fixtures</li>
  </ul>

  <h3>Can I use LightGroove without an ArtNet node?</h3>
  <p>LightGroove is designed to work with ArtNet, so you'll need an ArtNet-to-DMX interface to control physical fixtures. However, you can use it for testing and development with software DMX visualizers that support ArtNet input.</p>

  <h3>What ArtNet interfaces are compatible?</h3>
  <p>LightGroove works with any ArtNet-to-DMX interface, including:</p>
  <ul>
    <li>Enttec ODE (Open DMX Ethernet)</li>
    <li>DMXking eDMX1, eDMX2, eDMX4</li>
    <li>Artistic Licence Net-Lynx series</li>
    <li>Any other device supporting ArtNet protocol</li>
  </ul>

  <h3>Why won't the web UI open?</h3>
  <p>Try these steps:</p>
  <ul>
    <li>Check if the server is running (look for terminal output)</li>
    <li>Manually navigate to <a href="http://localhost:5555" target="_blank" rel="noopener">http://localhost:5555</a></li>
    <li>Check if another program is using port 5555</li>
    <li>Try a different web browser</li>
    <li>Check firewall settings</li>
  </ul>

  <h3>Can I change the port from 5555?</h3>
  <p>Yes, you can modify the port in <code>main.py</code>. Look for the line that starts the Flask server and change the port parameter.</p>

  <h2>Configuration</h2>

  <h3>Where are the configuration files?</h3>
  <p>All configuration files are in the <code>config/</code> directory:</p>
  <ul>
    <li><code>fixtures.json</code> - Fixture profiles</li>
    <li><code>patch.json</code> - Fixture patching</li>
    <li><code>artnet.json</code> - ArtNet nodes and universe mapping</li>
    <li><code>colors.json</code> - Color definitions</li>
  </ul>

  <h3>Can I edit configuration without restarting?</h3>
  <p>Yes! Use the Config tab in the web UI to edit settings. Changes are saved automatically and the server reloads without requiring a manual restart.</p>

  <h3>How do I add a new fixture type?</h3>
  <p>You can add fixtures in two ways:</p>
  <ol>
    <li>Edit <code>config/fixtures.json</code> manually - define channels and their offsets</li>
    <li>Use the Config tab in the web UI (future feature)</li>
  </ol>
  <p>Refer to your fixture's manual for its channel layout.</p>

  <h3>What if my fixture isn't in the fixture library?</h3>
  <p>LightGroove doesn't have a built-in fixture library. You need to create a custom fixture profile in <code>fixtures.json</code> based on your fixture's DMX channel layout from its manual.</p>

  <h3>How many fixtures can I control?</h3>
  <p>You can control as many fixtures as your DMX universes allow (512 channels per universe). Add multiple universes and ArtNet nodes to control larger setups.</p>

  <h2>DMX & ArtNet</h2>

  <h3>I'm not getting any DMX output. What's wrong?</h3>
  <p>Check these common issues:</p>
  <ul>
    <li>Is the ArtNet node IP address correct in the Config tab?</li>
    <li>Is the ArtNet node powered on and connected to the network?</li>
    <li>Are the computer and ArtNet node on the same network?</li>
    <li>Is the universe mapping configured correctly?</li>
    <li>Are fixtures patched in <code>patch.json</code>?</li>
    <li>Is the Master fader above 0%?</li>
    <li>Check firewall settings (UDP port 6454 for ArtNet)</li>
  </ul>

  <h3>What's the difference between DMX universe and ArtNet universe?</h3>
  <p>A DMX universe is a logical grouping of 512 channels. An ArtNet universe is how that DMX data is transmitted over the network. LightGroove maps DMX universes to ArtNet nodes and their universe numbers.</p>

  <h3>Can I use multiple ArtNet nodes?</h3>
  <p>Yes! Add multiple nodes in the Config tab, each with its own IP address and universe number. Map your DMX universes to different nodes as needed.</p>

  <h3>Why should I use Ethernet instead of WiFi?</h3>
  <p>Wired Ethernet provides more reliable, lower-latency communication than WiFi. For professional applications, always use wired connections for ArtNet nodes to avoid dropouts and timing issues.</p>

  <h3>What's the maximum cable length for DMX?</h3>
  <p>Standard DMX512 recommends a maximum cable run of 1,000 feet (300 meters). For longer runs, use DMX repeaters or boosters. Always use proper DMX-rated cables, not audio cables.</p>

  <h3>Do I need a DMX terminator?</h3>
  <p>Terminators are recommended for long cable runs (over 150 feet) or when you have many fixtures daisy-chained. A terminator is a 120-ohm resistor plugged into the DMX output of the last fixture in the chain.</p>

  <h2>Using LightGroove</h2>

  <h3>What's the difference between static colors and color FX?</h3>
  <p><strong>Static colors</strong> set all fixtures to a single color instantly and stay that way until changed.</p>
  <p><strong>Color FX</strong> are dynamic effects that automatically change colors over time based on BPM settings. They run continuously on the server until stopped.</p>

  <h3>How do color effects work?</h3>
  <p>LightGroove has four color FX modes:</p>
  <ul>
    <li><strong>Random 1</strong> - All fixtures show the same random color, changing at BPM speed</li>
    <li><strong>Random 2</strong> - Each fixture gets a different random color at each beat</li>
    <li><strong>Random 3</strong> - Even/odd fixtures alternate with black (strobe effect)</li>
    <li><strong>Random 4</strong> - Chaser effect lighting one fixture at a time in sequence</li>
  </ul>

  <h3>What does the Master fader do?</h3>
  <p>The Master fader (0-100%) scales all DMX output proportionally. It acts as a global brightness control without changing your individual fader positions. Set it to 100% for full output or lower it to dim everything at once.</p>

  <h3>What are FX BPM and FX Fade?</h3>
  <p><strong>FX BPM</strong> (1-480) controls how fast color effects cycle. Higher BPM = faster changes.</p>
  <p><strong>FX Fade</strong> (0-100%) controls the smoothness of color transitions. 0% = instant changes, 100% = smooth fade over the entire beat interval.</p>

  <h3>Can I control individual channels?</h3>
  <p>Yes! The Faders tab shows all channels (Dimmer, R, G, B, W, etc.) for each fixture. Move the faders to adjust individual channel values from 0-255.</p>

  <h3>How do I create custom colors?</h3>
  <p>Use the Config tab to edit colors. Adjust the RGBW sliders (0.0-1.0 range) to create your desired color. You can also add new colors or remove existing ones.</p>

  <h3>Can I save and recall lighting scenes?</h3>
  <p>Scene saving is not currently built into LightGroove. This is a planned feature for a future update. For now, you can manually note down fader positions or use external scene control software via the HTTP API.</p>

  <h2>Performance & Troubleshooting</h2>

  <h3>The web UI is slow or unresponsive</h3>
  <p>Try these solutions:</p>
  <ul>
    <li>Close other browser tabs using a lot of resources</li>
    <li>Try a different web browser (Chrome/Edge recommended)</li>
    <li>Check if your computer is under heavy load</li>
    <li>Reduce the FPS setting in the Config tab if you have many universes</li>
  </ul>

  <h3>Lights are flickering or glitching</h3>
  <p>This usually indicates network or DMX signal issues:</p>
  <ul>
    <li>Use wired Ethernet instead of WiFi for ArtNet nodes</li>
    <li>Check DMX cable quality and connections</li>
    <li>Add a DMX terminator to the last fixture in the chain</li>
    <li>Reduce the FPS if network bandwidth is limited</li>
    <li>Ensure proper grounding of fixtures and cables</li>
  </ul>

  <h3>Colors don't look right</h3>
  <p>Color accuracy depends on several factors:</p>
  <ul>
    <li>Verify color definitions in <code>colors.json</code> are correct</li>
    <li>Different fixtures may have different color mixing characteristics</li>
    <li>Check if fixtures need calibration</li>
    <li>Ensure Master fader is at 100% for full color saturation</li>
  </ul>

  <h3>Can I run LightGroove 24/7?</h3>
  <p>Yes, LightGroove is designed to be stable for continuous operation. However, for production environments, consider using a dedicated computer and monitoring for any issues.</p>

  <h2>Advanced Usage</h2>

  <h3>Does LightGroove have an API?</h3>
  <p>Yes! LightGroove exposes a REST API for external control. Endpoints include:</p>
  <ul>
    <li><code>GET /api/state</code> - Get current state</li>
    <li><code>POST /api/master</code> - Set master level</li>
    <li><code>POST /api/color</code> - Set color</li>
    <li><code>POST /api/fader</code> - Control individual channels</li>
  </ul>
  <p>See <code>src/http_api.py</code> for full API documentation.</p>

  <h3>Can I integrate LightGroove with other software?</h3>
  <p>Yes, through the HTTP API or by sending ArtNet data to LightGroove (if you configure it to receive). You can also use LightGroove alongside other lighting software since ArtNet supports multiple controllers.</p>

  <h3>Can I add MIDI control?</h3>
  <p>MIDI support is not currently built-in, but you could add it by modifying the source code or using external software to convert MIDI to HTTP API calls.</p>

  <h3>How do I contribute to LightGroove?</h3>
  <p>Contributions are welcome! Fork the repository on GitHub, make your changes, and submit a pull request. See <code>DEVELOPMENT.md</code> for development setup and guidelines.</p>

  <h2>Licensing & Support</h2>

  <h3>What license is LightGroove under?</h3>
  <p>LightGroove is released under the GNU Affero General Public License v3.0 (AGPL-3.0), which allows free use, modification, and distribution for both personal and commercial purposes. If you modify and deploy LightGroove as a network service, you must make your modified source code available to users.</p>

  <h3>Is there commercial support available?</h3>
  <p>LightGroove is a community-driven open-source project. Support is available through GitHub Issues and Discussions, but there is no official commercial support.</p>

  <h3>Where can I get help?</h3>
  <p>For help with LightGroove:</p>
  <ul>
    <li>Check the <a href="{{ '/docs' | relative_url }}">Documentation</a></li>
    <li>Browse the <a href="{{ '/glossary' | relative_url }}">Glossary</a> for terminology</li>
    <li>Search <a href="https://github.com/{{ site.repository }}/issues" target="_blank" rel="noopener">GitHub Issues</a></li>
    <li>Ask in <a href="https://github.com/{{ site.repository }}/discussions" target="_blank" rel="noopener">GitHub Discussions</a></li>
    <li>Open a new issue with details about your problem</li>
  </ul>

  <h3>Can I request features?</h3>
  <p>Absolutely! Open a feature request on the <a href="https://github.com/{{ site.repository }}/issues" target="_blank" rel="noopener">GitHub Issues</a> page. Describe what you'd like to see and why it would be useful.</p>

  <h2>Still Have Questions?</h2>
  
  <p>If you didn't find your answer here, please:</p>
  <ul>
    <li>Check the <a href="{{ '/docs' | relative_url }}">full documentation</a></li>
    <li>Browse the <a href="{{ '/glossary' | relative_url }}">glossary</a> for technical terms</li>
    <li>Ask in <a href="https://github.com/{{ site.repository }}/discussions" target="_blank" rel="noopener">GitHub Discussions</a></li>
    <li>Open an issue on <a href="https://github.com/{{ site.repository }}/issues" target="_blank" rel="noopener">GitHub</a></li>
  </ul>
</div>
