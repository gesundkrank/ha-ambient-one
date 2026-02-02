# Reverse Engineering Ambient One API

This guide walks through capturing and analyzing the Ambient Works API using mitmproxy.

## Step 1: Install mitmproxy

```bash
# Using homebrew (macOS)
brew install mitmproxy

# Or using pip
pip install mitmproxy
```

## Step 2: Start mitmproxy

```bash
# Start mitmproxy web interface (easier to use)
mitmweb --set block_global=false

# Or use the terminal interface
mitmproxy
```

This will:
- Start a proxy on `localhost:8080`
- Open a web interface at `http://127.0.0.1:8081`

## Step 3: Configure Browser Proxy

### Option A: Use Firefox (Recommended - easiest)
1. Open Firefox Settings → Network Settings
2. Choose "Manual proxy configuration"
3. HTTP Proxy: `127.0.0.1`, Port: `8080`
4. Check "Also use this proxy for HTTPS"
5. Click OK

### Option B: Use Chrome with Proxy Extension
1. Install "Proxy SwitchyOmega" extension
2. Configure proxy: `127.0.0.1:8080` for HTTP and HTTPS

## Step 4: Install mitmproxy Certificate

To intercept HTTPS traffic, you need to trust mitmproxy's certificate:

1. With proxy configured, visit: `http://mitm.it`
2. Download the certificate for your platform (macOS: click the Apple icon)
3. **macOS**:
   - Double-click the downloaded certificate
   - Add it to "System" keychain
   - Open Keychain Access, find "mitmproxy"
   - Double-click → Trust → "Always Trust"

## Step 5: Capture API Traffic

1. Start mitmproxy: `mitmweb`
2. Configure browser proxy (see Step 3)
3. Navigate to `https://app.ambientworks.io/`
4. Log in with your credentials
5. Navigate around the app to trigger API calls:
   - View your devices
   - Check air quality data
   - View historical data
   - Change settings

## Step 6: Analyze Captured Traffic

Look for:
- **API Base URL**: Usually `api.ambientworks.io` or similar
- **Authentication**: Look for:
  - `Authorization` header with Bearer tokens
  - Cookie-based auth
  - API keys in headers or query params
- **Key Endpoints**:
  - Device list: `/api/devices` or `/api/v1/devices`
  - Device data: `/api/devices/{id}/data`
  - Real-time data: WebSocket connections
  - Historical data: `/api/devices/{id}/history`

## Step 7: Save the Flows

In mitmweb:
1. Filter for `ambientworks.io` in the filter box
2. Select relevant requests
3. File → Save → "flows" format
4. Save as `ambient_api_capture.mitm`

Or export as HAR:
1. File → Export → "HAR"
2. Save as `ambient_api_capture.har`

## Step 8: Clean Up

After capturing:
1. Disable proxy in your browser
2. Stop mitmproxy (Ctrl+C)
3. You can optionally remove the certificate from Keychain Access

## Next Steps

Once you have captured the API traffic, we'll:
1. Analyze the authentication flow
2. Document the API endpoints
3. Create a Python client library
4. Build the Home Assistant integration
