#!/usr/bin/env python3
"""Extract Supabase API details from HAR file."""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def extract_supabase_api(har_path: Path):
    """Extract Supabase API information."""
    with open(har_path) as f:
        har = json.load(f)

    supabase_base = None
    api_key = None
    auth_token = None
    device_id = None

    endpoints = {}

    for entry in har['log']['entries']:
        url = entry['request']['url']

        if 'supabase.co' not in url:
            continue

        parsed = urlparse(url)

        if not supabase_base:
            supabase_base = f"{parsed.scheme}://{parsed.netloc}"

        # Extract auth headers
        for header in entry['request']['headers']:
            if header['name'].lower() == 'apikey' and not api_key:
                api_key = header['value']
            elif header['name'].lower() == 'authorization' and not auth_token:
                auth_token = header['value']

        # Extract device ID from URLs
        if 'device_id' in url:
            query = parse_qs(parsed.query)
            if 'device_id' in query:
                device_id = query['device_id'][0].replace('in.(', '').replace(')', '').replace('eq.', '')

        # Store endpoint info
        path = parsed.path
        method = entry['request']['method']
        key = f"{method} {path}"

        if key not in endpoints:
            endpoints[key] = {
                'method': method,
                'path': path,
                'sample_url': url,
                'status': entry['response']['status'],
                'responses': []
            }

        # Try to get response body
        try:
            if entry['response']['content'].get('text'):
                response_text = entry['response']['content']['text']
                response_data = json.loads(response_text)
                if response_data:  # Only store non-empty responses
                    endpoints[key]['responses'].append(response_data)
        except:
            pass

    # Print results
    print("="*80)
    print("SUPABASE API CONFIGURATION")
    print("="*80)
    print(f"\n🌐 Supabase URL: {supabase_base}")
    print(f"\n🔑 API Key (anon): {api_key[:50]}..." if api_key else "No API key found")
    print(f"\n🔐 Auth Token: {auth_token[:50]}..." if auth_token else "No auth token found")
    print(f"\n📱 Device ID: {device_id}" if device_id else "No device ID found")

    print("\n" + "="*80)
    print("API ENDPOINTS")
    print("="*80)

    for key, info in sorted(endpoints.items()):
        print(f"\n{key}")
        print(f"  Status: {info['status']}")
        print(f"  Sample URL: {info['sample_url']}")

        if info['responses']:
            response = info['responses'][0]
            if isinstance(response, list) and response:
                print(f"  Response: Array of {len(response)} items")
                print(f"  Sample item keys: {list(response[0].keys())}")
                print(f"  Sample item:")
                print(f"    {json.dumps(response[0], indent=6)}")
            elif isinstance(response, dict):
                print(f"  Response keys: {list(response.keys())}")
                print(f"  Sample:")
                print(f"    {json.dumps(response, indent=6)}")

    # Save structured output
    output = {
        'supabase_url': supabase_base,
        'api_key': api_key,
        'auth_token_sample': auth_token[:50] + '...' if auth_token else None,
        'device_id': device_id,
        'endpoints': endpoints
    }

    output_path = Path('supabase_api_config.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*80)
    print(f"\n✅ Configuration saved to: {output_path}")
    print("\n" + "="*80)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_supabase_api.py <har_file>")
        sys.exit(1)

    har_file = Path(sys.argv[1])
    if not har_file.exists():
        print(f"Error: File not found: {har_file}")
        sys.exit(1)

    extract_supabase_api(har_file)
