import argparse
from input_validation import validate_server_parameters, validate_client_parameters
import asyncio

from server import Server
from client import Client


def main() -> None:
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description='SCCTP Server',
                                                                  usage='%(prog)s [options]',
                                                                  epilog="For more help or information, visit us on discord at https://discord.gg/SC2EXYHA\n")
        parser.add_argument('action', type=str, help='The action to perform', choices=['client', 'server'])
        parser.add_argument('--broadcast', type=str, help='Your local broadcast address')
        parser.add_argument('--remote', type=str, help='The  hexternalost IP address')
        parser.add_argument('--sip', type=str, help='The source IP address of the host\'s ps2')
        parser.add_argument('--players', type=str, help='Space separated hostnames or IPs of the players joining the game', nargs='+')
        parser.add_argument('--upnp', action=argparse.BooleanOptionalAction, help='Attempt to use UPnP to open a port on the router')
        parser.add_argument('--hpv2', action=argparse.BooleanOptionalAction, help='Test the hole punch v2 method')
        args: argparse.Namespace = parser.parse_args()

        if args.action == 'client':
            if not validate_client_parameters(args=args):
                return

            remote = args.remote
            broadcast = args.broadcast
            Client(remote=remote, broadcast=broadcast).listen()

        elif args.action == 'server':
            if not validate_server_parameters(args=args):
                return

            local_ps2 = args.sip
            players = args.players
            server = Server(local_ps2=local_ps2, players=players)
            if args.upnp:
                server.attempt_upnp()
            if not args.hpv2:
                server.hole_punch_fw()
            else:
                asyncio.run(server.hole_punch_fw_v2())

        else:
            print("Invalid action. Please choose either client or server.")
            return

    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error in main: {repr(e)}")


if __name__ == "__main__":
    main()
