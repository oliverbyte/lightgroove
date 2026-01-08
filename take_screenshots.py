#!/usr/bin/env python3
"""
Script to take screenshots of LightGroove UI programmatically.
Requires: pip install playwright && playwright install chromium
"""
import time
import subprocess
import sys
from pathlib import Path

def take_screenshots():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright not installed")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
    
    # Start the server in background
    print("Starting LightGroove server...")
    server_process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            
            # Navigate to the app
            print("Navigating to http://localhost:5555...")
            page.goto("http://localhost:5555")
            
            # Wait for content to load
            page.wait_for_selector(".tab", timeout=5000)
            time.sleep(2)  # Extra time for fixtures to render
            
            # Screenshot 1: Globals tab (default)
            print("Capturing Globals tab...")
            page.screenshot(path="img/screenshot_globals.png", full_page=False)
            
            # Click Faders tab
            print("Switching to Faders tab...")
            page.click("button[data-tab='faders']")
            time.sleep(1)  # Wait for tab transition
            
            # Screenshot 2: Faders tab
            print("Capturing Faders tab...")
            page.screenshot(path="img/screenshot_faders.png", full_page=False)
            
            # Click Colors tab
            print("Switching to Colors tab...")
            page.click("button[data-tab='colors']")
            time.sleep(1)  # Wait for tab transition
            
            # Screenshot 3: Colors tab
            print("Capturing Colors tab...")
            page.screenshot(path="img/screenshot_colors.png", full_page=False)
            
            browser.close()
            print("✓ Screenshots saved to img/")
            
    finally:
        # Stop the server
        print("Stopping server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✓ Done")

if __name__ == "__main__":
    take_screenshots()
