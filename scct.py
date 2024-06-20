from scapy.all import IP, UDP, Ether, sniff, sendp, Raw
import argparse
from ipaddress import ip_address
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# SCCTP Protocol Structure Example
# FIND_REQUEST
# eth - ffffffffffff00041f93fca70800
# ip - 4500003800000000401168140afdfca70afdffff
# udp - 03e903e9002460ae
# req_action - 53434c4950494e4700 - 12 bytes
# counter_inc - e0b03e - 3 bytes - decimal 14725182
# preamble - 13e339491565a8c631dd4c26 - 12 bytes
# postamble - 5eabad41 - 4 bytes

# FIND_RESPONSE
# eth - ffffffffffff00041f82a8fc0800
# ip - 4500008c000000004011bb6b0afda8fc0afdffff
# udp - 03e903e9007866d3
# res_action - 53535256494e464f00000000
# preamble - 13e339491565a8c631dd4c26 - 12 bytes
# game_info - ffffffff04000000010000000a00000000000000494e49303100083d43696e656d61003e00003843
#             0000404300008042000080430000c0420000083d4e5354494e435400000000000000000000000000 - 80 bytes
# postamble - 5eabad41 - 4 bytes
# trailer - 0000863c - 4 bytes

RES_ACTION: bytes = b'\x53\x53\x52\x56\x49\x4e\x46\x4f\x00\x00\x00\x00'  # SSRVINFO
RES_TRAILER: bytes = b'\x00\x00\x86\x3c'
PLAYER_HOST: bytes = b'\x53\x43\x43\x54\x50\x53\x32'  # SCCTPS2
GAME_INFO: bytes = (b'\xff\xff\xff\xff\x04\x00\x00\x00\x01\x00\x00\x00\x0a\x00\x00\x00\x00\x00\x00\x00'
                    b'\x49\x4e\x49\x30\x31\x00\x08\x3d\x43\x69\x6e\x65\x6d\x61\x00\x3e\x00\x00\x38\x43\x00\x00'
                    b'\x40\x43\x00\x00\x80\x42\x00\x00\x80\x43\x00\x00\xc0\x42\x00\x00\x08\x3d') + PLAYER_HOST + b'\x00' * 13
LOCAL_BROADCAST_ADDRESS: str = ''
EXTERNAL_GAME_HOST_IP: str = ''
COMMON_LOCAL_NETWORK_BC: list = ['192.168.0.255', '192.168.1.255']


def send_response_packet(preamble: bytes, postamble: bytes) -> None:
    try:
        # create the response packet with a dest of 10.253.255.255 and a source of the external game host ip
        # set the broadcast address to the common local network broadcast addresseses if LOCAL_BROADCAST_ADDRESS is not set
        broadcast_addresses = [LOCAL_BROADCAST_ADDRESS if bool(LOCAL_BROADCAST_ADDRESS) else x for x in COMMON_LOCAL_NETWORK_BC]
        for addr in broadcast_addresses:
            res_pkt = Ether(dst='ff:ff:ff:ff:ff:ff')/IP(dst=addr, src=EXTERNAL_GAME_HOST_IP)/UDP(sport=1001, dport=1001)/Raw()
            # poplate the load with the response fields via offsets
            new_payload = RES_ACTION + preamble + GAME_INFO + postamble + RES_TRAILER
            res_pkt[Raw].load = new_payload
            # send the response packet
            sendp(res_pkt, verbose=0)
    except Exception as e:
        print(f"Error in send_response_packet: {repr(e)}")


def parse_request_packet(pkt) -> None:
    try:
        # parse the packet load
        req_load: bytes = pkt[UDP].load
        # parse the request via byte offsets
        # req_action = req_load[0:9] # unused
        # counter_inc = req_load[9:12] # unused
        preamble: bytes = req_load[12:24]
        postamble: bytes = req_load[24:28]

        # send the response packet
        send_response_packet(preamble, postamble)
        print("FIND_REQUEST packet found and response sent. The game should now appear in your game list as Host: SCCTPS2.")

    except Exception as e:
        print(f"Error in parse_request_packet: {repr(e)}")


def build_banner() -> None:
    # Show the user the entered information in a text table
    print("\n---------------------")
    print("SCCTP Server Emulator")
    print("---------------------")
    print(f"EXTERNAL_GAME_HOST_IP: {EXTERNAL_GAME_HOST_IP}")
    print(f"LOCAL_BROADCAST_ADDRESS: {LOCAL_BROADCAST_ADDRESS if bool(LOCAL_BROADCAST_ADDRESS) else COMMON_LOCAL_NETWORK_BC}")
    print("Listening for SCCTP packets...\n")
    return


def main() -> None:
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description='SCCTP Server')
        parser.add_argument('--bc', type=str, help='The local broadcast address')
        parser.add_argument('--host', type=str, help='The host unique key', required=True)
        parser.add_argument('--password', type=str, help='The password for the lobby to join', required=True)
        args: argparse.Namespace = parser.parse_args()
        password = args.password
        password = password.encode('utf-8')

        salt = b'\xcdS:\x80\xdc\x8b)\x90IT\xd5\xbb\x93\x80\xc2\xd8'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(password))
        fernet = Fernet(key)
        decrypted_host = fernet.decrypt(args.host.encode('utf-8')).decode('utf-8')
        ip_address(decrypted_host)  # validate the IP address
        if args.bc:
            ip_address(args.bc)  # validate the IP address

        global EXTERNAL_GAME_HOST_IP, LOCAL_BROADCAST_ADDRESS
        EXTERNAL_GAME_HOST_IP = args.host
        LOCAL_BROADCAST_ADDRESS = args.bc if args.bc else None

        build_banner()

        # listen for udp packets using scapy coming from the 10.253.0.0/16 network
        sniff(lfilter=lambda x: x.haslayer(UDP) and x[UDP].sport == 1001 and x[Ether].dst == 'ff:ff:ff:ff:ff:ff' and len(x) == 70,
              prn=lambda x: parse_request_packet(x),
              count=100)

    except Exception as e:
        print(f"Error in main: {repr(e)}")


if __name__ == "__main__":
    main()
