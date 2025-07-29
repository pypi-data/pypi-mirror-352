# Akamai API

Official Python package for detecting Akamai CDN usage, analyzing HTTP headers, performing network scans, and interacting with Akamai APIs.

## Features

1. **Detection Utilities**
   - `is_akamai_ip(ip: str) -> bool` – Check if an IP belongs to Akamai via ASN lookup.
   - `has_akamai_cname(hostname: str) -> bool` – Determine if a domain CNAMEs to an Akamai edge hostname.

2. **Header Analysis**
   - `analyze_cache_headers(headers: dict) -> dict` – Extract cache status, cacheability, and true cache key from response headers.
   - `detect_bot_manager(headers: dict) -> bool` – Identify Akamai Bot Manager markers.
   - `detect_akamai_waf(status_code: int, headers: dict) -> bool` – Detect WAF blocks by status code and server header.

3. **Scanning Utilities**
   - `dns_lookup(name: str, record_type: str = 'A') -> list` – Perform DNS queries for various record types.
   - `identify_cdn_provider(hostname: str) -> str` – Infer CDN provider via DNS resolution and WHOIS.
   - `whois_lookup(query: str) -> dict` – Retrieve WHOIS/RDAP data for a domain or IP.

4. **Akamai API Integrations**
   - `purge_cache(identifiers: list, by: str = 'url', network: str = 'production') -> dict` – Invalidate Akamai edge cache.
   - `list_property_hostnames(property_name: str, version: int) -> list` – List hostnames in a Property Manager configuration.
   - `list_edns_zones() -> list` – Retrieve configured Edge DNS zones.
   - `list_cps_certificates() -> list` – List SSL certificates managed by CPS.

## Installation

Install via PyPI:
```bash
pip install akamai-api
```

Install from Git:
```
pip install git+https://github.com/akamai-packages/akamai-api.git
```

## Quickstart Examples

Place your credentials in an EdgeGrid resource file, .edgerc, under a heading of [default] at your local home directory.
```
 [default]
 client_secret = C113nt53KR3TN6N90yVuAgICxIRwsObLi0E67/N8eRN=
 host = akab-h05tnam3wl42son7nktnlnnx-kbob3i3v.luna.akamaiapis.net
 access_token = akab-acc35t0k3nodujqunph3w7hzp7-gtm6ij
 client_token = akab-c113ntt0k3n4qtari252bfxxbsl-yvsdj
 ```

### 1. Detection and Header Analysis
```python
from akamai_api import (
    is_akamai_ip,
    has_akamai_cname,
    analyze_cache_headers,
    detect_bot_manager,
    detect_akamai_waf
)
import requests

# Check if an IP belongs to Akamai
print(is_akamai_ip('104.81.0.1'))  # True or False

# Check if a hostname CNAMEs to Akamai
print(has_akamai_cname('www.example.com'))

# Fetch a URL and analyze Akamai-related headers
resp = requests.get('https://www.example.com')
cache_info = analyze_cache_headers(resp.headers)
bot_managed = detect_bot_manager(resp.headers)
waf_blocked = detect_akamai_waf(resp.status_code, resp.headers)

print('Cache Info:', cache_info)
print('Bot Manager Detected:', bot_managed)
print('WAF Blocked:', waf_blocked)
```

### 2. Network Scanning
```python
from akamai_api import dns_lookup, identify_cdn_provider, whois_lookup

# DNS lookup for CNAME records
print(dns_lookup('www.example.com', 'CNAME'))

# Identify CDN provider via DNS + WHOIS
print(identify_cdn_provider('www.reddit.com'))

# WHOIS data for an IP
info = whois_lookup('8.8.8.8')
print('Organization:', info.get('org'))
```

### 3. Akamai API Usage
```python
from akamai_api import purge_cache, list_property_hostnames, list_edns_zones, list_cps_certificates

# Purge URLs from the Akamai production network
result = purge_cache(['https://www.example.com/style.css'], by='url', network='production')
print('Purge Result:', result)

# List hostnames under a Property Manager property version
hostnames = list_property_hostnames('example_property', 5)
print('Property Hostnames:', hostnames)

# List Edge DNS zones
zones = list_edns_zones()
print('EDNS Zones:', zones)

# List CPS-managed SSL certificates
certs = list_cps_certificates()
print('CPS Certificates:', certs)
```

## CLI Usage
```python
# Detect if an IP is on Akamai
akamai-api detect-ip 104.81.0.1

# Purge a URL from Akamai
akamai-api purge --url https://www.example.com/logo.png --network production

# List property hostnames
akamai-api list-property --name example_property --version 5
```