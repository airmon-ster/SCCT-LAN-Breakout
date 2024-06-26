import threading
from time import sleep
import websockets
import websockets.sync.server
from scapy.all import UDP, sniff
from dataclasses import dataclass, field


g_websocket: websockets.sync.server.ServerConnection = None
g_stop_threads: bool = False


@dataclass
class Redirector:
    websocket: websockets.sync.server.ServerConnection = None

    def serve(self) -> None:
        print("Starting websocket server...")
        try:
            with websockets.sync.server.serve(self.handler, "0.0.0.0", 8765) as server:
                print("Websocket server started...")
                server.serve_forever()

        except Exception as e:
            print(f"Error in serve: {repr(e)}")

    def handler(self, websocket):
        global g_websocket, g_stop_threads
        g_websocket = websocket
        g_stop_threads = False
        try:
            print("Client connected...")
            raw_listener = Raw_listener()
            raw_listener_thread = threading.Thread(target=raw_listener.listen, daemon=True, args=('Listener', lambda: g_stop_threads))
            raw_listener_thread.start()

            refresh_thread = threading.Thread(target=raw_listener.refresh_ports, daemon=True, args=('Port Refresh', lambda: g_stop_threads))
            refresh_thread.start()

        except websockets.ConnectionClosed:
            print("Connection closed")
            g_websocket = None
            g_stop_threads = True
        except Exception as e:
            print(f"Error in handler: {repr(e)}")
            g_websocket = None
            g_stop_threads = True
        finally:
            for thread in [raw_listener_thread, refresh_thread]:
                thread.join()


@dataclass
class Raw_listener:
    punch_ports: list[int] = field(default_factory=lambda: [10070, 10071, 10072, 10073, 10074, 10075, 10076, 10077, 10078, 10079, 10080])

    def listen(self, t, stop):
        print("Starting listener...")
        try:
            while True:
                sniff(lfilter=lambda x: x.haslayer(UDP) and x[UDP].dport == 3658,
                      prn=lambda x: self.send_packet(x), count=100)
                if stop():
                    print(f"Stopping {t} thread...")
                    break
        except Exception as e:
            print(f"Error in listen: {repr(e)}")

    def send_packet(self, pkt):
        global g_stop_threads
        try:
            if isinstance(pkt, str):
                g_websocket.send(pkt)
                return

            sport = str(pkt[UDP].sport)
            if sport in self.punch_ports:
                return

            print(f"Received packet: {pkt.summary()}")
            g_websocket.send(sport)
            self.punch_ports.append(sport)
        except websockets.ConnectionClosed:
            g_stop_threads = True
        except Exception as e:
            print(f"Error in send_packet: {repr(e)}")

    def refresh_ports(self, t, stop):
        try:
            while True:
                sleep(15)
                print("Refreshing ports...")
                self.punch_ports.clear()
                if stop():
                    print(f"Stopping {t} thread...")
                    break
        except Exception as e:
            print(f"Error in refresh_ports: {repr(e)}")

    # on init, send the default ports ahead of time
    def __post_init__(self):
        for port in self.punch_ports:
            self.send_packet(str(port))


def main():
    try:
        redirector = Redirector()
        server_thread = threading.Thread(target=redirector.serve, daemon=True)
        server_thread.start()

        # This thread is going to serve forever, so we are blocking main here
        server_thread.join()

    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
