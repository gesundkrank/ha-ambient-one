# Ambient One Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant custom integration for the **Ambient One** air quality sensor from Ambient Works.

## Features

- 🌡️ **Complete Air Quality Monitoring**: PM1.0, PM2.5, PM4.0, PM10, CO2, VOC, NOx
- 📊 **Indoor Air Quality Score**: 0-10 scale with category (Good/Moderate/Poor/Severe)
- 🌡️ **Environmental Sensors**: Temperature and Humidity
- 🔋 **Device Diagnostics**: Battery level, WiFi signal strength, firmware version
- 🏠 **Native Home Assistant Integration**: Config flow setup, automatic device discovery
- ⚡ **Real-time Updates**: Polls every 60 seconds for fresh data
- 📱 **Air Quality Entity**: Unified air quality platform support

## Monitored Parameters

Each Ambient One device provides:

| Sensor | Unit | Description |
|--------|------|-------------|
| PM1.0 | µg/m³ | Particulate Matter 1.0 |
| PM2.5 | µg/m³ | Particulate Matter 2.5 |
| PM4.0 | µg/m³ | Particulate Matter 4.0 |
| PM10 | µg/m³ | Particulate Matter 10 |
| CO2 | ppm | Carbon Dioxide |
| VOC Index | - | Volatile Organic Compounds Index |
| NOx Index | - | Nitrogen Oxides Index |
| Temperature | °C | Ambient Temperature |
| Humidity | % | Relative Humidity |
| IAQ Score | 0-10 | Indoor Air Quality Score |
| AQI Category | - | Good/Moderate/Poor/Severe |
| Battery | % | Battery Level |
| WiFi Signal | dBm | Signal Strength |

## Installation

### HACS (Recommended)

1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `https://github.com/gesundkrank/ha-ambient-one`
4. Category: Integration
5. Click "Download"
6. Restart Home Assistant

### Manual Installation

```bash
cd /config/custom_components
git clone https://github.com/gesundkrank/ha-ambient-one ambient_one
```

Then restart Home Assistant.

## Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Ambient One**
4. Enter your Ambient Works credentials:
   - **Email**: Your Ambient Works account email
   - **Password**: Your account password

The integration will automatically discover all your Ambient One devices.

## Screenshots

Coming soon!

## How It Works

This integration uses the Ambient Works Supabase API to fetch data from your Ambient One devices:

- **Authentication**: Email/password authentication via Supabase Auth
- **API Backend**: Supabase PostgREST API
- **Update Frequency**: Every 60 seconds
- **Data Source**: `sensor_averages` table with minute-level aggregation

## Technical Details

The integration was built by reverse-engineering the Ambient Works web app API. Key endpoints:

- `POST /auth/v1/token` - Authentication
- `GET /rest/v1/devices` - Device list
- `GET /rest/v1/sensor_averages` - Historical sensor data
- `GET /rest/v1/sensor_realtime` - Real-time IAQ score
- `GET /rest/v1/device_events` - Air quality events

For developers interested in the reverse engineering process, see [REVERSE_ENGINEERING.md](REVERSE_ENGINEERING.md).

## Troubleshooting

### Integration won't add

- Verify credentials at https://app.ambientworks.io/
- Check Home Assistant logs: `Settings → System → Logs`

### No entities appearing

- Ensure your device is online in the Ambient Works app
- Wait 1-2 minutes for first data refresh
- Check if entities are disabled: `Settings → Devices & Services → Ambient One → Device`

### Stale data

- The device updates every 60 seconds
- If the device is offline, `last_seen` will show the last successful update

## Development

### Project Structure

```
custom_components/ambient_one/
├── __init__.py          # Integration setup & coordinator
├── manifest.json        # Integration metadata
├── const.py            # Constants
├── config_flow.py      # UI configuration flow
├── api.py              # Ambient One API client
├── sensor.py           # Sensor platform
├── air_quality.py      # Air quality platform
├── strings.json        # UI strings
└── translations/
    └── en.json         # English translations
```

### Running Locally

```bash
# Link to your Home Assistant config
ln -s $(pwd)/custom_components/ambient_one /config/custom_components/

# Restart Home Assistant
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/gesundkrank/ha-ambient-one/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/gesundkrank/ha-ambient-one/discussions)

## Disclaimer

This is an unofficial integration and is not affiliated with, endorsed by, or connected to Ambient Works. Use at your own risk.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- **API Reverse Engineering**: Done using mitmproxy
- **Device**: Ambient One by [Ambient Works](https://www.ambientworks.io/)
- **Home Assistant**: [home-assistant.io](https://www.home-assistant.io/)
