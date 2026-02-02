# Quick Start Guide

## 🚀 Get it on GitHub (5 minutes)

### 1. Initialize Git & Commit

```bash
./setup_github.sh
```

### 2. Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `ha-ambient-one`
3. Description: `Home Assistant integration for Ambient One air quality sensor`
4. Make it **Public** (required for HACS)
5. **Don't** check "Add README" (we have one)
6. Click "Create repository"

### 3. Push to GitHub

```bash
git remote add origin https://github.com/gesundkrank/ha-ambient-one.git
git branch -M main
git push -u origin main
```

### 4. Create First Release

1. Go to: https://github.com/gesundkrank/ha-ambient-one/releases/new
2. Tag: `v1.0.0`
3. Release title: `v1.0.0 - Initial Release`
4. Description:
   ```
   Initial release of Ambient One Home Assistant integration.

   Features:
   - Complete air quality monitoring (PM1.0, PM2.5, PM4.0, PM10, CO2, VOC, NOx)
   - Temperature and humidity sensors
   - Indoor Air Quality Score (0-10)
   - Battery and WiFi signal monitoring
   - Config flow UI setup
   - Air quality platform support
   - Updates every 60 seconds
   ```
5. Click "Publish release"

### 5. Enable GitHub Features

Go to: https://github.com/gesundkrank/ha-ambient-one/settings

- ✅ Issues
- ✅ Discussions (optional but nice to have)

---

## 🏠 Test Locally First (Recommended)

### Quick Test

```bash
# Copy integration to Home Assistant
cp -r custom_components/ambient_one /config/custom_components/

# Restart Home Assistant
# Then: Settings → Devices & Services → + Add Integration → "Ambient One"
```

### What to Check

1. Integration appears in available integrations
2. Config flow accepts your email/password
3. Device is created with your device name
4. All sensor entities show data
5. Values match the Ambient Works app
6. No errors in logs

See [TESTING.md](TESTING.md) for detailed testing checklist.

---

## 📦 Install via HACS

Once on GitHub:

### Add to HACS

1. Home Assistant → HACS → Integrations
2. Click ⋮ (menu) → Custom repositories
3. Add URL: `https://github.com/gesundkrank/ha-ambient-one`
4. Category: **Integration**
5. Click "Add"

### Install

1. Search for "Ambient One" in HACS
2. Click "Download"
3. Restart Home Assistant
4. Add integration: Settings → Devices & Services → + Add Integration

---

## 🔧 Quick Commands

```bash
# Check files are ready
ls custom_components/ambient_one/

# Verify no placeholder text remains
grep -r "jan-grassegger" . --exclude-dir=.git

# Test the API client directly
python3 -c "
from custom_components.ambient_one.api import AmbientOneClient
import asyncio

async def test():
    async with AmbientOneClient('your@email.com', 'password') as client:
        devices = await client.get_devices()
        print(f'Found {len(devices)} device(s)')

asyncio.run(test())
"

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/gesundkrank/ha-ambient-one.git
git push -u origin main
```

---

## 📚 Documentation Reference

- **README.md** - Full project overview
- **INSTALLATION.md** - Installation guide
- **TESTING.md** - Testing and validation
- **REVERSE_ENGINEERING.md** - How we built the API client

---

## ❓ Troubleshooting

### "Integration not found" in Home Assistant

- Make sure files are in: `/config/custom_components/ambient_one/`
- Restart Home Assistant completely
- Check logs for errors

### "Invalid authentication"

- Test credentials at: https://app.ambientworks.io/
- Make sure there are no typos in email/password
- Check Home Assistant logs for detailed error

### No sensor data appearing

- Wait 1-2 minutes after setup (initial data fetch)
- Verify device is online in Ambient Works app
- Check entity states in Developer Tools → States

---

## 🎉 You're Done!

Your integration is ready to:
- ✅ Install locally
- ✅ Push to GitHub
- ✅ Share via HACS
- ✅ Share with the community

Questions? Open an issue on GitHub!
