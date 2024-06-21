from validators import domain
from socket import gethostbyname
from ipaddress import ip_address
import argparse


def validate_players(players: list[str]) -> bool:
    try:
        for player in players:
            if domain(player):
                player = gethostbyname(player)
            ip_address(player)
        return True

    except Exception as e:
        print(f"Error in validate_players: {repr(e)}")
        return False


def validate_server_parameters(args: argparse.Namespace) -> bool:
    try:
        if not args.sip:
            print("You must specify the source IP address of the host's PS2.")
            return False

        if not args.players:
            print("You must specify the players joining the game. Example: --players airmonster.com 1.1.1.1 player.duckdns.com")
            return False

        if not validate_players(players=args.players):
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
