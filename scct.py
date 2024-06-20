import argparse
from ipaddress import ip_address
import validators
from socket import gethostbyname

import client
import server

SCRIPT_TYPE: str = ''
EXTERNAL_GAME_HOST_IP: str = ''
LOCAL_BROADCAST_ADDRESS: str = ''
LOCAL_PS2_MAC: str = ''
LOCAL_PS2_IP: str = ''
PLAYERS: list[str] = []


def main() -> bool:
    try:
        global SCRIPT_TYPE, EXTERNAL_GAME_HOST_IP, LOCAL_BROADCAST_ADDRESS, LOCAL_PS2_MAC, PLAYERS, LOCAL_PS2_IP
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description='SCCTP Server',
                                                                  usage='%(prog)s [options]',
                                                                  epilog="For more help or information, visit us on discord at https://discord.gg/SC2EXYHA")
        parser.add_argument('action', type=str, help='The action to perform', choices=['client', 'server'])
        parser.add_argument('--broadcast', type=str, help='Your local broadcast address')
        parser.add_argument('--remote', type=str, help='The external host IP address')
        parser.add_argument('--mac', type=str, help='Your PS2\'s MAC address')
        parser.add_argument('--sip', type=str, help='The source IP address of the host\'s ps2')
        parser.add_argument('--players', type=str, help='Space separated hostname\s or IP\s of the players joining the game', nargs='+')
        args: argparse.Namespace = parser.parse_args()

        if args.action == 'client':
            SCRIPT_TYPE = 'client'
            if not args.remote:
                print("You must specify the external host IP address.")
                return False

            EXTERNAL_GAME_HOST_IP = args.remote
            LOCAL_BROADCAST_ADDRESS = args.broadcast if args.broadcast else None
            if validators.domain(EXTERNAL_GAME_HOST_IP):
                EXTERNAL_GAME_HOST_IP = gethostbyname(EXTERNAL_GAME_HOST_IP)
            ip_address(EXTERNAL_GAME_HOST_IP)  # validate the IP address
            if LOCAL_BROADCAST_ADDRESS:
                ip_address(LOCAL_BROADCAST_ADDRESS)  # validate the IP address

        else:
            SCRIPT_TYPE = 'server'
            if not args.mac:
                print("You must specify the PS2's MAC address.")
                return False
            if not args.sip:
                print("You must specify the source IP address of the host's PS2.")
                return False

            if not args.players:
                print("You must specify the players joining the game. Example: --players 1.1.1.1 2.2.2.2 test.duckdns.com")
                return False

            LOCAL_PS2_MAC = args.mac
            LOCAL_PS2_IP = args.sip
            PLAYERS = args.players
            for player in args.players:
                if validators.domain(player):
                    player = gethostbyname(player)
                ip_address(player)

        return True

    except Exception as e:
        print(f"Error in main: {repr(e)}")
        return False


if __name__ == "__main__":
    if main():
        if SCRIPT_TYPE == 'client':
            # client code
            client.listen(EXTERNAL_GAME_HOST_IP, LOCAL_BROADCAST_ADDRESS)
        else:
            # server code
            server.punch(LOCAL_PS2_MAC, LOCAL_PS2_IP, PLAYERS)
