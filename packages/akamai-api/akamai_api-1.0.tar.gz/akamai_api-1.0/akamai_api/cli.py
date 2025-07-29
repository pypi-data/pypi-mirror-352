import argparse
import sys
from .core import (
    is_akamai_ip,
    purge_cache,
    list_property_hostnames,
)

def main():
    parser = argparse.ArgumentParser(prog='akamai-api', description='Akamai API CLI')
    subparsers = parser.add_subparsers(dest='command')

    # detect-ip
    detect_parser = subparsers.add_parser('detect-ip', help='Check if IP belongs to Akamai')
    detect_parser.add_argument('ip', help='IP address to check')

    # purge
    purge_parser = subparsers.add_parser('purge', help='Purge URLs or CP codes')
    purge_parser.add_argument('--url', help='URL to purge')
    purge_parser.add_argument('--cpcode', help='CP code to purge')
    purge_parser.add_argument('--network', choices=['production', 'staging'], default='production')

    # list-property
    list_parser = subparsers.add_parser('list-property', help='List property hostnames')
    list_parser.add_argument('--name', required=True, help='Property Manager property name')
    list_parser.add_argument('--version', type=int, required=True, help='Property version number')

    args = parser.parse_args()

    if args.command == 'detect-ip':
        if is_akamai_ip(args.ip):
            print(f"{args.ip} is an Akamai IP")
        else:
            print(f"{args.ip} is NOT an Akamai IP")

    elif args.command == 'purge':
        identifiers = []
        if args.url:
            identifiers.append(args.url)
        elif args.cpcode:
            identifiers.append(args.cpcode)
        else:
            print("Error: Provide --url or --cpcode to purge")
            sys.exit(1)
        result = purge_cache(identifiers, by='url' if args.url else 'cpcode', network=args.network)
        print("Purge response:", result)

    elif args.command == 'list-property':
        hostnames = list_property_hostnames(args.name, args.version)
        print("Property Hostnames:")
        for h in hostnames:
            print("-", h)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
