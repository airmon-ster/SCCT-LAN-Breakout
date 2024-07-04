from dataclasses import field, dataclass
from scapy.all import IP, UDP, Ether, sendp, Raw
import websockets
import validators
from socket import gethostbyname
import base64


TEST_KEEP_ALIVE = b'\xff' * 1200

# TEST_KEEP_ALIVE needs to be blocked on the signal server firewall so it doesnt ever reach the gamer
# iptables -t raw -A PREROUTING -p udp --sport 3658 -m length --length 1100:1300 -j DROP

# Gamer traffic needs to pass through the signal server to the game host
# iptables -t nat -I PREROUTING 1 -p udp --dport 3658 -j DNAT --to-destination <host external ip>
# iptables -t nat -A POSTROUTING -p udp --dport 3658 -j MASQUERADE


@dataclass
class Server:
    local_ps2: str
    signal: str
    timeout: int = field(default=20)
    ports: list[int] = field(default_factory=lambda: [10070, 10071, 10072, 10073, 10074, 10075, 10076, 10077, 10078, 10079, 10080])

    async def hole_punch_fw(self) -> None:
        try:
            if validators.domain(self.signal):
                self.signal = gethostbyname(self.signal)
            print(f"Connected to the signal server: {self.signal}. Waiting for clients to connect.")
            async for websocket in websockets.connect(f"ws://{self.signal}:8765", ping_interval=None):
                try:
                    while True:
                        punch_port = str(await websocket.recv())
                        print(f"Received port to hole-punch: {punch_port}")
                        pkt = Ether()/IP(dst=self.signal, src=self.local_ps2)/UDP(sport=3658, dport=int(punch_port))/Raw()
                        pkt[Raw].load = TEST_KEEP_ALIVE
                        sendp(pkt, verbose=0)
                        print(f"Sent keep alive packet to {self.signal} on port {punch_port}")
                except websockets.ConnectionClosed:
                    print("Connection Closed. Reconnecting...")
        except Exception as e:
            print(f"Error in hole_punch_fw: {repr(e)}")

    def __post_init__(self) -> None:
        build_server_banner(self)


def obfuscate_ip(ip: str) -> str:
    # Encode the IP address using Base64
    encoded_ip = base64.urlsafe_b64encode(ip.encode())
    return encoded_ip.decode()


def build_server_banner(server: Server) -> None:
    # Show the user the entered information in a text table
    print("\n---------------------")
    print("SCCTP FW Hole Puncher")
    print("---------------------")
    print(f"Local PS2: {server.local_ps2}")
    if server.timeout:
        print(f"Timeout: {server.timeout}")
    print(f"Signal Server: {server.signal}")
    print("---------------------")
