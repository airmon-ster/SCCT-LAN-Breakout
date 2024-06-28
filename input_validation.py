from validators import domain
from socket import gethostbyname
from ipaddress import ip_address
import argparse


def validate_signal_ips(signal: str, ps: str) -> bool:
    try:
        for ip in [signal, ps]:
            if domain(ip):
                ip = gethostbyname(ip)
            ip_address(ip)
        return True

    except Exception as e:
        print(f"Error in validate_signal: {repr(e)}")
        return False


def validate_server_parameters(args: argparse.Namespace) -> bool:
    try:
        if not args.ps:
            print("You must specify the source IP address of the host's PS2.")
            return False

        if not args.signal:
            print("You must specify the signal server. Example: --signal testserver.scct.airmon-ster.com")
            return False

        if not validate_signal_ips(signal=args.signal, ps=args.ps):
            return False
        return True

    except Exception as e:
        print(f"Error in validate_server_parameters: {repr(e)}")
        return False


def validate_client_parameters(args: argparse.Namespace) -> bool:
    try:
        if not args.remote:
            print("You must specify the external host IP address.")
            return False
        if domain(args.remote):
            args.remote = gethostbyname(args.remote)
        ip_address(args.remote)

        return True
    except Exception as e:
        print(f"Error in validate_client_parameters: {repr(e)}")
        return False
