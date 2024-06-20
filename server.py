from dataclasses import field, dataclass
from time import sleep
from scapy.all import IP, UDP, Ether, sendp, Raw
import validators
from socket import gethostbyname
import sys


@dataclass
class Server:
    local_ps2: str
    players: list[str]
    ports: list[int] = field(default_factory=lambda: [10070, 10071, 10072, 10073, 10074, 10075])

    def hole_punch_fw(self) -> None:
        try:
            while True:
                # Build a scapy packet with the PS2 MAC address and IP address and send it to the players ip addresses to open a hole in server firewall
                for player in self.players:
                    if validators.domain(player):
                        player = gethostbyname(player)
                    sys.stdout.write('.')  # Print a dot for each player
                    for port in self.ports:
                        pkt = Ether()/IP(dst=player, src=self.local_ps2)/UDP(sport=3658, dport=port)/Raw((b'\x73\x70\x6C\x69\x6E\x74\x65\x72\x63\x65\x6C'
                                                                                                          b'\x6C\x6F\x6E\x6C\x69\x6E\x65\x2E\x6E\x65\x74'))  # splintercellonline.net
                        sendp(pkt, verbose=0)
                sleep(30)

        except Exception as e:
            print(f"Error in hole_punch_fw: {repr(e)}")

    def __post_init__(self) -> None:
        build_server_banner(self)
        self.hole_punch_fw()


def build_server_banner(server: Server) -> None:
    # Show the user the entered information in a text table
    print("\n---------------------")
    print("SCCTP FW Hole Puncher")
    print("---------------------")
    print(f"Local PS2: {server.local_ps2}")
    print("Players:")
    for player in server.players:
        print(f"  {player}")
    print("---------------------")
