---
layout: default
title: LightGroove - Modern DMX Lighting Controller
description: Control your lighting setup with ease using LightGroove's web-based interface. Real-time fader control, color effects, and ArtNet output.
---

<section class="hero">
  <div class="container">
    <h1>Control Your Lights with Ease</h1>
    <p class="subtitle">Modern DMX lighting controller with intuitive web-based UI</p>
    <div class="cta-buttons">
      <a href="https://github.com/{{ site.repository }}/releases" class="btn btn-primary">Download Now</a>
      <a href="{{ '/installation' | relative_url }}" class="btn btn-secondary">Get Started</a>
    </div>
  </div>
</section>

<section class="features-section">
  <div class="container">
    <h2 class="section-title">Powerful Features</h2>
    <p class="section-subtitle">Everything you need to control your lighting setup professionally</p>
    
    <div class="feature-grid">
      <div class="feature-card">
        <span class="feature-icon">🎛️</span>
        <h3>Real-Time Control</h3>
        <p>Control every fixture with precision using intuitive web-based faders. See DMX values update in real-time as you adjust.</p>
      </div>
      
      <div class="feature-card">
        <span class="feature-icon">🎨</span>
        <h3>Color Effects</h3>
        <p>Built-in color effects including static colors and dynamic FX modes. Create stunning light shows with chase effects and smooth transitions.</p>
      </div>
      
      <div class="feature-card">
        <span class="feature-icon">🌐</span>
        <h3>ArtNet Output</h3>
        <p>Send DMX via ArtNet to any compatible interface. Works seamlessly with professional lighting equipment and nodes.</p>
      </div>
      
      <div class="feature-card">
        <span class="feature-icon">⚡</span>
        <h3>Master Control</h3>
        <p>Global intensity scaling for all fixtures. Perfect for quick brightness adjustments without changing individual fader positions.</p>
      </div>
      
      <div class="feature-card">
        <span class="feature-icon">🎵</span>
        <h3>BPM Sync</h3>
        <p>Sync color effects to your desired tempo from 1-480 BPM. Adjustable fade time for smooth color transitions.</p>
      </div>
      
      <div class="feature-card">
        <span class="feature-icon">⚙️</span>
        <h3>Web Config</h3>
        <p>Configure everything through the web interface. Edit ArtNet nodes, colors, universe mapping, and more without touching config files.</p>
      </div>
    </div>
    
    <div style="text-align: center; margin-top: 3rem;">
      <a href="{{ '/features' | relative_url }}" class="btn btn-primary">Explore All Features</a>
    </div>
  </div>
</section>

<section class="screenshots-section">
  <div class="container">
    <h2 class="section-title">Beautiful Interface</h2>
    <p class="section-subtitle">Clean, modern design that makes lighting control a pleasure</p>
    
    <div class="screenshot-grid">
      <div class="screenshot-item">
        <img src="{{ '/img/screenshot_globals.png' | relative_url }}" alt="Global Controls Interface">
        <div class="screenshot-caption">Global Controls - Master intensity, BPM, and fade settings</div>
      </div>
      
      <div class="screenshot-item">
        <img src="{{ '/img/screenshot_faders.png' | relative_url }}" alt="Faders Interface">
        <div class="screenshot-caption">Faders - Real-time fixture control with live DMX values</div>
      </div>
      
      <div class="screenshot-item">
        <img src="{{ '/img/screenshot_colors.png' | relative_url }}" alt="Colors Interface">
        <div class="screenshot-caption">Colors - Static colors and dynamic effects</div>
      </div>
      
      <div class="screenshot-item">
        <img src="{{ '/img/screenshot_config.png' | relative_url }}" alt="Configuration Interface">
        <div class="screenshot-caption">Config - Web-based configuration editor</div>
      </div>
    </div>
  </div>
</section>

<section class="install-section">
  <div class="container">
    <h2 class="section-title">Quick Installation</h2>
    <p class="section-subtitle">Get up and running in minutes</p>
    
    <div class="install-methods">
      <div class="install-card">
        <h3>🪟 Windows</h3>
        <p class="description">Download the installer and run. It's that simple!</p>
        <a href="https://github.com/{{ site.repository }}/releases" class="btn btn-primary" style="display: inline-block; margin-top: 1rem;">Download Installer</a>
      </div>
      
      <div class="install-card">
        <h3>🍎 macOS</h3>
        <p class="description">Install via Homebrew:</p>
        <pre><code>brew tap oliverbyte/lightgroove \
  https://github.com/oliverbyte/lightgroove.git
brew install --HEAD \
  oliverbyte/lightgroove/lightgroove
lightgroove</code></pre>
      </div>
      
      <div class="install-card">
        <h3>🐍 From Source</h3>
        <p class="description">For developers and contributors:</p>
        <pre><code>git clone https://github.com/{{ site.repository }}.git
cd lightgroove
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py</code></pre>
      </div>
    </div>
    
    <div style="text-align: center; margin-top: 3rem;">
      <a href="{{ '/installation' | relative_url }}" class="btn btn-primary">Detailed Installation Guide</a>
    </div>
  </div>
</section>
