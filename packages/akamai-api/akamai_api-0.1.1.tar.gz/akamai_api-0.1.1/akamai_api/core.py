"""
Akamai Analysis Package Core Module
Contains detection, analysis, scanning, and API wrapper functions.
"""

import socket
import dns.resolver
import ipwhois
import whois as pywhois
import requests
from akamai.edgegrid import EdgeGridAuth
from configparser import ConfigParser

# Load EdgeGrid credentials from .edgerc
def get_akamai_session():
    """
    Returns a requests session with EdgeGridAuth loaded from .edgerc
    """
    config = ConfigParser()
    config.read('.edgerc')
    section = 'default'
    if not config.has_section(section):
        raise ValueError("Missing [default] section in .edgerc file")
    
    session = requests.Session()
    session.auth = EdgeGridAuth(
        client_token=config.get(section, 'client_token'),
        client_secret=config.get(section, 'client_secret'),
        access_token=config.get(section, 'access_token')
    )
    session.headers['Host'] = config.get(section, 'host')
    return session, config.get(section, 'host')

# 1. Detection Utilities

def is_akamai_ip(ip: str) -> bool:
    """
    Check if the given IP belongs to Akamai by IP WHOIS ASN lookup.
    """
    try:
        obj = ipwhois.IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        org = res.get('network', {}).get('name', '').lower()
        return 'akamai' in org
    except Exception:
        return False


def has_akamai_cname(hostname: str) -> bool:
    """
    Determine if a hostname CNAMEs to an Akamai edge domain.
    """
    try:
        answers = dns.resolver.resolve(hostname, 'CNAME', raise_on_no_answer=False)
        for r in answers:
            target = r.target.to_text().lower()
            if any(domain in target for domain in ['akamai.net', 'akamaiedge.net', 'edgesuite.net']):
                return True
        return False
    except Exception:
        return False

# 2. Header Analysis Functions

def analyze_cache_headers(headers: dict) -> dict:
    """
    Parse HTTP response headers to extract Akamai cache details.
    """
    return {
        'cache_hit': headers.get('X-Cache', '').endswith('_HIT'),
        'x_cache': headers.get('X-Cache'),
        'cacheable': headers.get('X-Check-Cacheable'),
        'true_cache_key': headers.get('X-True-Cache-Key'),
    }


def detect_bot_manager(headers: dict) -> bool:
    """
    Detect Akamai Bot Manager markers in HTTP headers.
    """
    return any('akamai-bot' in k.lower() for k in headers)


def detect_akamai_waf(status_code: int, headers: dict) -> bool:
    """
    Identify if Akamai WAF blocked the request (403 + Akamai server header).
    """
    if status_code == 403 and 'akamai' in headers.get('Server', '').lower():
        return True
    return False

# 3. Scanning Utilities

def dns_lookup(name: str, record_type: str = 'A') -> list:
    """
    Perform DNS queries for a given record type (A, AAAA, CNAME, etc.).
    """
    try:
        answers = dns.resolver.resolve(name, record_type)
        return [r.to_text() for r in answers]
    except Exception:
        return []


def identify_cdn_provider(hostname: str) -> str:
    """
    Infer CDN provider by IP resolution + WHOIS ASN lookup.
    """
    ips = dns_lookup(hostname)
    if not ips:
        return None
    ip = ips[0]
    try:
        obj = ipwhois.IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        return res.get('network', {}).get('remarks', [{}])[0].get('description')
    except Exception:
        return None


def whois_lookup(query: str) -> dict:
    """
    Perform WHOIS lookup for a domain or IP and return parsed data.
    """
    try:
        w = pywhois.whois(query)
        return w.__dict__
    except Exception:
        return {}

# 4. Akamai API Utilities

def purge_cache(identifiers: list, by: str = 'url', network: str = 'production') -> dict:
    """
    Purge or invalidate content via Akamai CCU/Purge API.
    """
    session, host = get_akamai_session()

    endpoint = f'https://{host}/ccu/v3/{by}/{network}'
    payload = {'objects': identifiers}
    resp = session.post(endpoint, json=payload)
    return resp.json()


def list_property_hostnames(property_name: str, version: int) -> list:
    """
    List hostnames configured in a Property Manager property version.
    """
    session, host = get_akamai_session()
    
    endpoint = f'https://{host}/papi/v1/properties/{property_name}/versions/{version}/hostnames'
    resp = session.get(endpoint)
    data = resp.json()
    return [h['cnameFrom'] for h in data.get('hostnames', {}).get('items', [])]


def list_edns_zones() -> list:
    """
    Retrieve Edge DNS zones via Akamai EDNS API.
    """
    session, host = get_akamai_session()

    endpoint = f'https://{host}/edgedns/v1/zones'
    resp = session.get(endpoint)
    return [z['zone'] for z in resp.json().get('zones', [])]


def list_cps_certificates() -> list:
    """
    List certificates managed by Akamai CPS.
    """
    session, host = get_akamai_session()

    endpoint = f'https://{host}/cps/v2/enrollments'
    resp = session.get(endpoint)
    return resp.json().get('enrollments', [])