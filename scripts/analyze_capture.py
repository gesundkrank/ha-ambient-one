#!/usr/bin/env python3
"""
Analyze mitmproxy capture to extract Ambient Works API details.

Usage:
    python scripts/analyze_capture.py <capture_file>

Supports:
    - .mitm (mitmproxy flow format)
    - .har (HTTP Archive format)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def analyze_har_file(har_path: Path) -> Dict[str, Any]:
    """Analyze HAR file for API patterns."""
    with open(har_path) as f:
        har = json.load(f)

    api_calls = []
    domains = set()
    auth_methods = set()
    endpoints = defaultdict(list)

    for entry in har['log']['entries']:
        request = entry['request']
        response = entry['response']
        url = request['url']

        # Filter for ambientworks.io domains
        if 'ambientworks.io' not in url:
            continue

        # Extract domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domains.add(parsed.netloc)

        # Extract auth headers
        auth_headers = {}
        for header in request['headers']:
            name = header['name'].lower()
            if name in ['authorization', 'x-api-key', 'x-auth-token', 'cookie']:
                auth_methods.add(f"{name}: {header['value'][:50]}...")
                auth_headers[name] = header['value']

        # Extract endpoint pattern
        path = parsed.path
        endpoint_key = f"{request['method']} {path}"

        # Parse request/response bodies
        req_body = None
        if request.get('postData'):
            try:
                req_body = json.loads(request['postData'].get('text', '{}'))
            except:
                req_body = request['postData'].get('text', '')

        resp_body = None
        if response.get('content'):
            try:
                resp_body = json.loads(response['content'].get('text', '{}'))
            except:
                resp_body = response['content'].get('text', '')

        api_calls.append({
            'method': request['method'],
            'url': url,
            'path': path,
            'status': response['status'],
            'auth_headers': auth_headers,
            'request_body': req_body,
            'response_body': resp_body,
        })

        endpoints[endpoint_key].append({
            'url': url,
            'status': response['status'],
            'sample_response': resp_body,
        })

    return {
        'domains': sorted(domains),
        'auth_methods': sorted(auth_methods),
        'endpoints': dict(endpoints),
        'api_calls': api_calls,
        'total_calls': len(api_calls),
    }


def print_analysis(analysis: Dict[str, Any]):
    """Pretty print the analysis results."""
    print("\n" + "="*80)
    print("AMBIENT WORKS API ANALYSIS")
    print("="*80)

    print(f"\n📊 Total API Calls Captured: {analysis['total_calls']}")

    print("\n🌐 Domains Found:")
    for domain in analysis['domains']:
        print(f"  • {domain}")

    print("\n🔐 Authentication Methods:")
    for auth in analysis['auth_methods']:
        print(f"  • {auth}")

    print("\n📡 API Endpoints Discovered:")
    for endpoint, calls in sorted(analysis['endpoints'].items()):
        print(f"\n  {endpoint}")
        print(f"    Called {len(calls)} time(s)")

        # Show sample response structure
        sample = calls[0].get('sample_response')
        if sample and isinstance(sample, dict):
            print(f"    Response keys: {list(sample.keys())}")

    print("\n" + "="*80)
    print("\n💾 Full details saved to: api_analysis.json")
    print("\nNext steps:")
    print("  1. Review the api_analysis.json file")
    print("  2. Identify device data endpoints")
    print("  3. Document the authentication flow")
    print("  4. Create Python API client")
    print("="*80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_capture.py <capture_file.har>")
        print("\nCapture file can be:")
        print("  - .har (HTTP Archive format) - Export from mitmweb")
        sys.exit(1)

    capture_file = Path(sys.argv[1])

    if not capture_file.exists():
        print(f"Error: File not found: {capture_file}")
        sys.exit(1)

    print(f"Analyzing: {capture_file}")

    if capture_file.suffix == '.har':
        analysis = analyze_har_file(capture_file)
    else:
        print(f"Error: Unsupported file format: {capture_file.suffix}")
        print("Please export as .har format from mitmweb")
        sys.exit(1)

    # Save full analysis
    output_file = Path('api_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    # Print summary
    print_analysis(analysis)


if __name__ == '__main__':
    main()
