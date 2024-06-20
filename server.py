from scapy.all import IP, UDP, Ether, sniff, sendp, Raw
import validators
from socket import gethostbyname

LOCAL_PS2_MAC: str = ''
LOCAL_PS2_IP: str = ''
PLAYERS: list[str] = []
PORTS: list[int] = [10071, 10072, 10073]


def build_server_banner() -> None:
    # Show the user the entered information in a text table
    print("\n---------------------")
    print("SCCTP FW Hole Puncher")
    print("---------------------")
    return


def hole_punch_fw() -> None:
    try:
        while True:
            # Build a scapy packet with the PS2 MAC address and IP address and send it to the players ip addresses to open a hole in server firewall
            for player in PLAYERS:
                if validators.domain(player):
                    player = gethostbyname(player)
                for port in PORTS:
                    pkt = Ether(src=LOCAL_PS2_MAC)/IP(dst=player, src=LOCAL_PS2_IP)/UDP(sport=3658, dport=port)/Raw()
                    sendp(pkt, verbose=0)
    except Exception as e:
        print(f"Error in hole_punch_fw: {repr(e)}")


def punch(mac: str, sip: str, players: list) -> None:
    global LOCAL_PS2_MAC, PLAYERS, LOCAL_PS2_IP
    LOCAL_PS2_MAC = mac
    LOCAL_PS2_IP = sip
    PLAYERS = players
    try:
        build_server_banner()

        hole_punch_fw()

    except Exception as e:
        print(f"Error in punch: {repr(e)}")

if __name__ == "__main__":
    print("Script cannot be run directly. Please run scct.py server instead.")