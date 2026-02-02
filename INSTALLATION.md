# Installation Guide

## HACS Installation (Recommended)

1. **Add Custom Repository:**
   - Open HACS in Home Assistant
   - Go to "Integrations"
   - Click the three dots menu (top right) → "Custom repositories"
   - Add repository URL: `https://github.com/gesundkrank/ha-ambient-one`
   - Select category: "Integration"
   - Click "Add"

2. **Install Integration:**
   - Search for "Ambient One Air Quality" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Configure:**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Ambient One"
   - Enter your Ambient Works credentials (email and password)

## Manual Installation

1. **Copy Files:**
   ```bash
   cd /config
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/gesundkrank/ha-ambient-one ambient_one
   ```

2. **Restart Home Assistant**

3. **Configure:**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Ambient One"
   - Enter your Ambient Works credentials

## What Gets Created

After setup, the integration creates the following entities for each Ambient One device:

### Sensors
- **PM1.0** - Particulate Matter 1.0 (µg/m³)
- **PM2.5** - Particulate Matter 2.5 (µg/m³)
- **PM4.0** - Particulate Matter 4.0 (µg/m³)
- **PM10** - Particulate Matter 10 (µg/m³)
- **CO2** - Carbon Dioxide (ppm)
- **VOC Index** - Volatile Organic Compounds Index
- **NOx Index** - Nitrogen Oxides Index
- **Temperature** - Ambient Temperature (°C)
- **Humidity** - Relative Humidity (%)
- **Indoor Air Quality Score** - Overall IAQ (0-10 scale)
- **Air Quality Category** - Good/Moderate/Poor/Severe
- **Battery** - Battery level (%)
- **WiFi Signal** - WiFi signal strength (dBm)

### Air Quality Entity
- Unified air quality entity with PM2.5, PM10, and CO2 levels
- Shows overall air quality index
- Includes all pollutants as attributes

## Troubleshooting

### Integration won't add
- Verify your Ambient Works credentials at https://app.ambientworks.io/
- Check Home Assistant logs for error messages

### No data showing
- Ensure your Ambient One device is online
- Check that you can see data in the Ambient Works mobile/web app
- Wait 1-2 minutes for the first data update

### Entities disabled by default
- Some entities (like WiFi Signal) are disabled by default
- Enable them in Settings → Devices & Services → Ambient One → Device → Enable entity

## Update Interval

The integration polls the Ambient One API every 60 seconds for updates.

## Support

For issues, feature requests, or contributions:
- GitHub: https://github.com/gesundkrank/ha-ambient-one/issues
