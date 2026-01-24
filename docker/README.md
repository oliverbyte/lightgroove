# LightGroove - Free Open Source DMX Lighting Controller

**Professional DMX lighting control made accessible for everyone.**

Web-based lighting controller featuring real-time fader control, dynamic color effects, and intuitive configuration. Built with Python and Flask, providing professional-grade DMX control through ArtNet output.

## Features

- **Web-Based UI** - Control from any device with a browser
- **ArtNet Output** - Professional DMX over network
- **Real-Time Control** - Instant fader and effect adjustments
- **Color Effects** - Multiple FX programs with BPM sync
- **Moving Head Support** - Full pan/tilt control with movement patterns
- **Multiple Universes** - Support for complex lighting setups
- **Auto-Save State** - Remembers your settings on restart

## Quick Start

**Prerequisites:** Docker installed on your system

**Get configuration files:**
```bash
mkdir -p ~/lightgroove && cd ~/lightgroove
git clone --depth 1 --filter=blob:none --sparse https://github.com/oliverbyte/lightgroove.git temp
cd temp && git sparse-checkout set config && mv config .. && cd .. && rm -rf temp
```

**Run container:**
```bash
docker run -d \
  --name lightgroove \
  -p 5555:5555 \
  -p 6454:6454/udp \
  -v $(pwd)/config:/app/config \
  --restart unless-stopped \
  oliverbyte/lightgroove:latest
```

**Access UI:** Open http://localhost:5555

## Configuration

All config files in `~/lightgroove/config/` are persistent:
- `artnet.json` - ArtNet nodes (edit via Config tab)
- `fixtures.json` - Fixture definitions
- `patch.json` - Fixture patching  
- `colors.json` - Color definitions (edit via Config tab)

Changes are immediately reflected in the running container.

## Links

- **Website:** https://oliverbyte.github.io/lightgroove/
- **Source Code:** https://github.com/oliverbyte/lightgroove
- **Documentation:** https://oliverbyte.github.io/lightgroove/docs
- **Issues/Support:** https://github.com/oliverbyte/lightgroove/issues

## License

MIT License - Free and open source
