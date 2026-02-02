# Testing the Integration

## Local Testing in Home Assistant

### 1. Copy to Home Assistant

```bash
# If your HA is on the same machine
cp -r custom_components/ambient_one /config/custom_components/

# Or create a symbolic link
ln -s $(pwd)/custom_components/ambient_one /config/custom_components/ambient_one
```

### 2. Restart Home Assistant

```bash
# From Home Assistant UI
Settings → System → Restart

# Or from CLI
ha core restart
```

### 3. Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Ambient One**
4. Enter your credentials
5. Verify the setup succeeds

### 4. Check Entities

After setup, you should see:

**Device**: Named after your Ambient One device (e.g., "Studio")

**Entities** (13 total per device):
- `sensor.studio_pm2_5` - PM2.5 level
- `sensor.studio_pm1_0` - PM1.0 level
- `sensor.studio_pm4_0` - PM4.0 level
- `sensor.studio_pm10` - PM10 level
- `sensor.studio_co2` - CO2 level
- `sensor.studio_voc_index` - VOC Index
- `sensor.studio_nox_index` - NOx Index
- `sensor.studio_temperature` - Temperature
- `sensor.studio_humidity` - Humidity
- `sensor.studio_indoor_air_quality_score` - IAQ Score
- `sensor.studio_air_quality_category` - Category (Good/Moderate/Poor/Severe)
- `sensor.studio_battery` - Battery level
- `sensor.studio_wifi_signal` - WiFi signal (disabled by default)
- `air_quality.studio_air_quality` - Unified air quality entity

## Verify Data Updates

### Check Logs

```bash
# From Home Assistant UI
Settings → System → Logs

# Filter for ambient_one
# Look for:
# - "Successfully authenticated with Ambient One API"
# - No error messages
```

### Monitor Sensor Updates

1. Go to **Developer Tools** → **States**
2. Find your sensor entities (e.g., `sensor.studio_pm2_5`)
3. Click on one to see details
4. Check:
   - State value is a number (not "Unknown" or "Unavailable")
   - `last_updated` timestamp refreshes every 60 seconds
   - Attributes show device_id, firmware_version, etc.

### Test Air Quality Entity

1. Go to **Developer Tools** → **States**
2. Find `air_quality.studio_air_quality`
3. Verify:
   - `air_quality_index` has a value
   - `particulate_matter_2_5` has a value
   - `particulate_matter_10` has a value
   - `carbon_dioxide` has a value
   - Attributes include all sensor readings

## Common Issues

### "Invalid Authentication"

- Double-check credentials at https://app.ambientworks.io/
- Verify you can log in to the web app
- Check for typos in email/password

### "No Entities Created"

- Check logs for errors
- Verify device is online in Ambient Works app
- Wait 1-2 minutes after setup
- Try restarting Home Assistant

### "Unknown" or "Unavailable" States

- Device may be offline
- Check `last_seen` attribute on device
- Verify device shows data in Ambient Works app
- Check Home Assistant logs for API errors

### WiFi Signal sensor not showing

- This entity is disabled by default
- Enable it: Settings → Devices & Services → Ambient One → [Device] → Enable entity

## API Rate Limits

The integration polls every 60 seconds. Supabase free tier limits:

- **API requests**: 500,000/month
- **Active connections**: 500

With 60-second polling:
- Requests per day: ~1,440 per device
- Requests per month: ~43,200 per device
- **You can have ~11 devices** before hitting limits

## Debug Mode

Enable debug logging to see API calls:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.ambient_one: debug
```

This will log:
- Authentication attempts
- API requests/responses
- Coordinator updates
- Error details

## Manual API Testing

You can test the API directly with the script:

```python
import asyncio
from custom_components.ambient_one.api import AmbientOneClient

async def test():
    async with AmbientOneClient("your@email.com", "password") as client:
        # Get devices
        devices = await client.get_devices()
        print(f"Found {len(devices)} devices")

        for device in devices:
            print(f"\nDevice: {device.name} ({device.device_id})")

            # Get sensor data
            data = await client.get_sensor_data(device.device_id)
            if data:
                print(f"  PM2.5: {data.pm2_5} µg/m³")
                print(f"  CO2: {data.co2} ppm")
                print(f"  IAQ Score: {data.iaq_score}")

asyncio.run(test())
```

## Validation Checklist

Before considering the integration complete:

- [ ] Integration appears in Settings → Devices & Services
- [ ] Config flow completes successfully
- [ ] Device is created with correct name
- [ ] All 13+ entities are created
- [ ] Sensor values match Ambient Works app
- [ ] Values update every 60 seconds
- [ ] Attributes show correct device info
- [ ] No errors in Home Assistant logs
- [ ] Air quality entity shows correct data
- [ ] Device info shows firmware version
- [ ] Battery percentage is correct

## Next Steps

Once testing is complete:

1. Push to GitHub
2. Create a release
3. Test HACS installation
4. Share with community
