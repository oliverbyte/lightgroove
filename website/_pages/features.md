---
layout: default
title: Features - LightGroove
description: Explore all the powerful features of LightGroove DMX lighting controller - real-time control, color effects, ArtNet output, and web-based configuration
permalink: /features/
---

<div class="docs-content">
  <h1>Features</h1>
  <p class="lead">LightGroove provides professional-grade lighting control with an intuitive web interface. Control your fixtures in real-time, create dynamic effects, and configure everything through your browser.</p>
  
  <h2>DMX / ArtNet Output</h2>
  <ul>
    <li><strong>ArtNet Protocol Support</strong> - Sends lighting data via industry-standard ArtNet protocol to any compatible network node or monitoring software</li>
    <li><strong>Universal Compatibility</strong> - Works seamlessly with any ArtNet-to-DMX interface including Enttec ODE, DMXking, Art-Net 4, and similar professional devices</li>
    <li><strong>Flexible Universe Mapping</strong> - Map any DMX universe to any ArtNet node and universe through the web UI (e.g., DMX universe 1 → ArtNet node 192.168.1.100 universe 0)</li>
    <li><strong>Multiple Node Support</strong> - Send to multiple ArtNet nodes simultaneously on different network addresses for large installations</li>
    <li><strong>Configurable Frame Rate</strong> - Adjust output FPS for optimal performance based on your setup</li>
  </ul>

  <h2>Web-Based User Interface</h2>
  
  <h3>Globals Tab</h3>
  <img src="{{ '/img/screenshot_globals.png' | relative_url }}" alt="Globals Interface - Master controls and flash button">
  <ul>
    <li><strong>Master Fader</strong> - Global intensity control (0-100%) that scales all DMX output in real-time without changing individual fader positions. Perfect for room brightness adjustments during shows.</li>
    <li><strong>FX BPM Control</strong> - Set the speed of color effects from 1-480 beats per minute for perfect music synchronization. From slow ambient (1 BPM) to fast strobing (480 BPM).</li>
    <li><strong>FX Fade</strong> - Adjust smooth color transitions from instant (0%) to full beat interval (100%). Create professional-looking crossfades between colors.</li>
    <li><strong>Flash Button</strong> - Press and hold for instant full white override. Automatically pauses running effects. Releases back to previous state. Touch-friendly for mobile control.</li>
  </ul>

  <h3>Faders Tab</h3>
  <img src="{{ '/img/screenshot_faders.png' | relative_url }}" alt="Faders Interface - Real-time per-channel control">
  <ul>
    <li><strong>Compact Fixture Cards</strong> - Clean, organized layout showing each patched fixture with all its channels in one place</li>
    <li><strong>Vertical Faders</strong> - Intuitive faders arranged in logical channel order (Dimmer, Red, Green, Blue, White) for precise control</li>
    <li><strong>Real-Time DMX Values</strong> - Live DMX values (0-255) displayed and updated instantly as you move faders</li>
    <li><strong>Responsive Layout</strong> - Automatically adapts to your screen width - works perfectly on desktop, tablet, and phone</li>
    <li><strong>Per-Channel Control</strong> - Independent control of every channel on every fixture for maximum flexibility</li>
    <li><strong>Clear Labels</strong> - Each fader clearly labeled with channel name and fixture identifier</li>
  </ul>

  <h3>Colors Tab</h3>
  <img src="{{ '/img/screenshot_colors.png' | relative_url }}" alt="Colors Interface - Static colors and dynamic effects">
  
  <h4>Static Colors</h4>
  <p>10 preset color buttons with instant one-click activation:</p>
  <ul>
    <li><strong>Standard Colors</strong> - Red, Green, Blue, Cyan, Magenta, Yellow</li>
    <li><strong>Additional Colors</strong> - White, Orange, Purple, Black (blackout)</li>
    <li><strong>Customizable</strong> - All colors defined with RGBW values (0.0-1.0 range) in <code>config/colors.json</code></li>
    <li><strong>Dynamic Buttons</strong> - Button backgrounds automatically display the actual RGBW color from your definitions</li>
    <li><strong>Active Indication</strong> - Currently active color highlighted with visual feedback</li>
    <li><strong>Add Your Own</strong> - Create custom colors through the Config tab with live preview</li>
  </ul>

  <h4>Color FX (Server-Side Effects)</h4>
  <p>Dynamic effects that run independently on the server, synchronized to BPM:</p>
  <ul>
    <li><strong>Random 1</strong> - Unified color wash: All fixtures display the same random color, cycling together at BPM speed. Perfect for creating cohesive color changes across your entire rig.</li>
    <li><strong>Random 2</strong> - Disco ball effect: Each fixture gets a different random color, all changing simultaneously at each beat. Creates dynamic, multi-color looks.</li>
    <li><strong>Random 3</strong> - Strobe effect: Alternates between even-numbered and odd-numbered patches with black, creating a pulsing strobe-like pattern.</li>
    <li><strong>Random 4</strong> - Sequential chaser: Lights one fixture at a time in sequence with random colors. Classic chase effect with color variety.</li>
    <li><strong>Smooth Fades</strong> - All effects support smooth fade transitions based on FX Fade setting (0-100%). Create professional crossfades instead of abrupt color changes.</li>
    <li><strong>Active Indication</strong> - Effect buttons highlight to show what's currently running</li>
    <li><strong>Multi-Color Display</strong> - Random 2/3/4 effects show all currently active colors in the button for visual feedback</li>
    <li><strong>Flash Integration</strong> - Effects automatically pause when flash button is held, resuming when released</li>
  </ul>

  <h3>Config Tab</h3>
  <img src="{{ '/img/screenshot_config.png' | relative_url }}" alt="Config Interface - Complete web-based configuration">
  <p>Complete web-based configuration system - no need to manually edit JSON files:</p>
  <ul>
    <li><strong>ArtNet Nodes Management</strong> - Add, edit, and delete ArtNet output nodes with IP addresses and universe numbers. Visual list of all configured nodes with edit/delete buttons for each.</li>
    <li><strong>Universe Mapping</strong> - Configure which DMX universe maps to which ArtNet node and universe. Easy dropdown selection for routing.</li>
    <li><strong>Colors Editor</strong> - Full color management system:
      <ul>
        <li>Edit RGBW color definitions using interactive sliders (0-1 range)</li>
        <li>Live color preview shows actual color as you adjust</li>
        <li>Add custom colors with any name you want</li>
        <li>Remove colors you don't need</li>
        <li>Changes immediately reflected in Colors tab buttons</li>
      </ul>
    </li>
    <li><strong>Global Settings</strong> - Configure system-wide options:
      <ul>
        <li>Default output mode (ArtNet/virtual DMX)</li>
        <li>Frames per second (FPS) for DMX output timing</li>
        <li>Performance tuning options</li>
      </ul>
    </li>
    <li><strong>Automatic Reload</strong> - All changes are saved immediately and the server reloads automatically. No manual restart required!</li>
    <li><strong>Zero Downtime</strong> - Continue working while configuration reloads. UI stays connected and operational.</li>
  </ul>

  <h2>Connection Monitoring & Recovery</h2>
  <ul>
    <li><strong>Real-Time Status</strong> - Visual connection indicator in header shows server status (green dot = connected, red pulsing = offline)</li>
    <li><strong>Automatic Recovery</strong> - UI automatically detects when server comes back online and reloads all data</li>
    <li><strong>Seamless Reconnection</strong> - No manual intervention needed - just keep working and the UI recovers automatically</li>
    <li><strong>Zero User Action</strong> - No need to refresh browser or restart application after connection restore</li>
  </ul>

  <h2>Configuration System</h2>
  <p>Flexible configuration system supports both web UI and direct file editing:</p>
  <ul>
    <li><code>config/fixtures.json</code> - Fixture profiles with channel definitions
      <ul>
        <li>Define fixture types (RGBW, RGB, dimmer-only, custom)</li>
        <li>Specify channel names, types, and default values</li>
        <li>Create reusable fixture profiles</li>
      </ul>
    </li>
    <li><code>config/patch.json</code> - Patched fixtures per universe
      <ul>
        <li>Assign fixtures to specific DMX addresses</li>
        <li>Organize fixtures across multiple universes</li>
        <li>Set per-fixture identifiers</li>
      </ul>
    </li>
    <li><code>config/artnet.json</code> - ArtNet configuration (editable via Config tab)
      <ul>
        <li>Define ArtNet node IP addresses and universes</li>
        <li>Map DMX universes to ArtNet nodes</li>
        <li>Configure multiple output destinations</li>
      </ul>
    </li>
    <li><code>config/colors.json</code> - Color definitions (editable via Config tab)
      <ul>
        <li>RGBW values 0.0-1.0 for each color</li>
        <li>Custom color names and presets</li>
        <li>Used by static color buttons and FX engine</li>
      </ul>
    </li>
  </ul>

  <h2>Technical Features</h2>
  <ul>
    <li><strong>Real-Time Performance</strong> - Low-latency DMX output with configurable frame rate (FPS). Optimized Python backend ensures responsive control.</li>
    <li><strong>Multiple Universes</strong> - Support for multiple DMX universes through ArtNet. Scale to hundreds of fixtures across many universes.</li>
    <li><strong>Flexible Fixture Profiles</strong> - Define any fixture type with custom channel layouts. Support for RGBW, RGB, single-channel dimmers, and complex moving lights.</li>
    <li><strong>Cross-Platform</strong> - Runs on Windows, macOS, and Linux. Python-based ensures compatibility across all major operating systems.</li>
    <li><strong>Self-Contained</strong> - Built-in Flask web server, no separate web server or database required. Everything runs from a single Python process.</li>
    <li><strong>RESTful API</strong> - Complete HTTP API for integration with other software, custom controllers, or automation systems.</li>
    <li><strong>Network Accessible</strong> - Control from any device on your network. Server runs on port 5555, accessible via http://localhost:5555 or your computer's IP address.</li>
    <li><strong>Modular Architecture</strong> - Clean separation between DMX controller, fixture manager, color FX engine, and HTTP API for easy customization and extension.</li>
    <li><strong>MIT Licensed</strong> - Completely open source with permissive licensing. Use commercially, modify, and distribute freely.</li>
  </ul>

  <h2>Use Cases</h2>
  <ul>
    <li><strong>Mobile DJs</strong> - Portable lighting control running on a laptop. Control from tablet while DJing. Perfect for wedding receptions, parties, and mobile events.</li>
    <li><strong>Small Venues</strong> - Affordable permanent installation for bars, clubs, and restaurants. No expensive lighting console required.</li>
    <li><strong>Live Events & Performances</strong> - Small to medium events, concerts, and shows. Quick setup and intuitive control for event technicians.</li>
    <li><strong>Theater Productions</strong> - Community theater and educational theater programs. Student productions and rehearsal spaces.</li>
    <li><strong>House Parties & Private Events</strong> - Turn any space into a party venue. Easy enough for anyone to operate.</li>
    <li><strong>Architectural Lighting</strong> - Permanent installations in commercial spaces, restaurants, or architectural features. Color-changing accent lighting.</li>
    <li><strong>Development & Testing</strong> - Test DMX fixtures during development. Verify fixture channel layouts and color mixing.</li>
    <li><strong>Education</strong> - Learn DMX lighting control concepts. Understand ArtNet protocol and lighting programming.</li>
    <li><strong>Home Automation Integration</strong> - Integrate lighting control into smart home systems via the HTTP API.</li>
  </ul>
  
  <h2>What's Next?</h2>
  <p>LightGroove is actively developed with new features planned:</p>
  <ul>
    <li><strong>MIDI Controller Support</strong> - Use physical MIDI controllers for tactile fader control</li>
    <li><strong>Scene Presets</strong> - Save and recall complete lighting states</li>
    <li><strong>Cue Lists</strong> - Program sequences of scenes with timing</li>
    <li><strong>Timeline Programming</strong> - Time-based automation for shows</li>
    <li><strong>Audio Reactive Effects</strong> - Effects that respond to music and sound input</li>
    <li><strong>Additional Fixture Profiles</strong> - Growing library of pre-defined fixtures</li>
  </ul>
  
  <p style="text-align: center; margin-top: 2rem;">
    <a href="{{ '/installation' | relative_url }}" class="btn btn-primary">Get Started Now</a>
    <a href="https://github.com/{{ site.repository }}/discussions" class="btn btn-secondary">Join Community</a>
  </p>
</div>
