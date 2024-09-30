import argparse
from input_validation import validate_server_parameters, validate_client_parameters
import asyncio

from server import Server
from client import Client
from da_client import DAClient

def main() -> None:
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description='SCCTP Server',
                                                                  usage='%(prog)s [options]',
                                                                  epilog="For more help or information, visit us on discord at https://discord.gg/SC2EXYHA\n")
        parser.add_argument('action', type=str, help='The action to perform', choices=['client', 'server'])
        parser.add_argument('--remote', type=str, help='The host external IP address')
        parser.add_argument('--ps', type=str, help='The source IP address of the host\'s ps2')
        parser.add_argument('--signal', type=str, help='Space separated hostnames or IPs of the players joining the game')
        parser.add_argument('--timeout', type=int, help='The timeout for the server hole punch method keep alives', default=20)
        parser.add_argument('--nic', type=str, help='The active network adapter to use.')
        parser.add_argument('--hostname', type=str, help='The host discord name.')
        parser.add_argument('--game', type=str, help='PS2 Game selection (CT/DA).')
        # parser.add_argument('--port', type=str, help='Port to send traffic to server.')
        args: argparse.Namespace = parser.parse_args()

        if args.action == 'client':
            if not validate_client_parameters(args=args):
                return
            if args.nic != '' and args.hostname != '':
                args.hostname=str(args.hostname).encode('ascii')
                print(args.hostname)
                if args.game == 'CT' or args.game == 'PT':
                    Client(remote=args.remote, iface=args.nic, hostname=args.hostname).listen()
                elif args.game == 'DA':
                    DAClient(remote=args.remote, iface=args.nic, hostname=args.hostname).listen()
            elif args.nic != '':
                if args.game == 'CT' or args.game == 'PT':
                    Client(remote=args.remote, iface=args.nic).listen()
                elif args.game == 'DA':
                    DAClient(remote=args.remote, iface=args.nic).listen()
            else:
                if args.game == 'CT' or args.game == 'PT':
                    Client(remote=args.remote).listen()
                elif args.game == 'DA':
                    DAClient(remote=args.remote).listen()

        elif args.action == 'server':
            if not validate_server_parameters(args=args):
                return
            if args.nic != '':
                server = Server(local_ps2=args.ps, signal=args.signal, timeout=args.timeout, iface=args.nic)
            else:
                server = Server(local_ps2=args.ps, signal=args.signal, timeout=args.timeout)
            asyncio.run(server.hole_punch_fw())

        else:
            print("Invalid action. Please choose either client or server.")
            return

    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error in main: {repr(e)}")


if __name__ == "__main__":
    main()
