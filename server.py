from dataclasses import field, dataclass
from time import sleep
from scapy.all import IP, UDP, Ether, sendp, Raw
import validators
from socket import gethostbyname
import sys

# UDP 100171 keep alive packet. Host sends this to client
# mac - 0008a20c0c9600041f82a8fc0800
# ip - 45000025e8ad000040118229c0a80a46261b1ee8 - identification field increments by 1 for each packet. This also changes the checksum
# udp - 27570e4a0011c611
# ka_header - 0700
# 4f4ceb2d47ad
# ka_trailer - 6b000000000000000000

SERVER_TO_CLIENT_KEEP_ALIVE = b'\x07\x00\x4f\x4c\xeb\x2d\x47\xad\x6b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


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
                        pkt = Ether()/IP(dst=player, src=self.local_ps2)/UDP(sport=3658, dport=port)/Raw()
                        pkt[Raw].load = SERVER_TO_CLIENT_KEEP_ALIVE
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
