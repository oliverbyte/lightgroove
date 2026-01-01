#!/usr/bin/env python3
"""
LightGroove - DMX RGBW PAR Controller (HTTP/Web UI only)
Main entry point
Author: https://github.com/oliverbyte
"""
import os
import sys
import time
import signal
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dmx_controller import DMXController
from fixture_manager import FixtureManager
from ui_generator import generate_ui
from http_api import HttpApiServer


def main():
    """Main application"""
    print("=" * 60)
    print("LightGroove - DMX RGBW PAR Controller (HTTP/Web UI)")
    print("=" * 60)
    
    # Configuration paths
    base_dir = Path(__file__).parent
    fixtures_file = base_dir / "config" / "fixtures.json"
    patch_file = base_dir / "config" / "patch.json"
    artnet_file = base_dir / "config" / "artnet.json"
    ui_dir = base_dir / "ui_dist"
    http_port = int(os.getenv("LIGHTGROOVE_HTTP_PORT", "5555"))
    
    print(f"\nConfiguration:")
    print(f"  Fixtures: {fixtures_file}")
    print(f"  Patch:    {patch_file}")
    print(f"  ArtNet:   {artnet_file}")
    print()
    
    http = None

    # Initialize components
    try:
        # DMX Controller with ArtNet support
        dmx = DMXController(config_file=str(artnet_file))
        dmx.start()
        
        # Fixture Manager
        fixture_mgr = FixtureManager(dmx, str(fixtures_file), str(patch_file))
        
        # Generate UI shell and start HTTP UI/API server
        generate_ui(fixture_mgr, ui_dir, api_base="")
        http = HttpApiServer(fixture_mgr, ui_dir, host="0.0.0.0", port=http_port)
        try:
            http.start()
        except OSError as e:
            print(f"HTTP UI/API: Failed to start on port {http_port}: {e}")
            raise
        
        print("\n✓ System ready!")
        print(f"  Available fixtures: {fixture_mgr.list_fixtures()}")
        print(f"  UI/API: http://0.0.0.0:{http_port} (serving {ui_dir})")
        print("Press Ctrl+C to exit\n")
        
        # Signal handler for clean shutdown
        def signal_handler(sig, frame):
            print("\n\nShutting down...")
            if http:
                http.stop()
            dmx.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running
        while True:
            time.sleep(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
