import threading
import websockets
import websockets.sync.server
from scapy.all import UDP, sniff
from dataclasses import dataclass

@dataclass
class Redirector:
    websocket: websockets.WebSocketServerProtocol = None
    ws_server: websockets.WebSocketServer = None

    def serve(self) -> None:
        print("Starting websocket server")
        try:
            with websockets.sync.server.serve(self.handler, "0.0.0.0", 8765) as server:
                print("Websocket server started")
                server.serve_forever()

        except Exception as e:
            print(f"Error in serve: {repr(e)}")

    def handler(self, websocket):
        try:
            self.websocket = websocket
            # dont close the connection
            while True:
                pass
        except websockets.ConnectionClosed:
            print("Connection closed")


@dataclass
class Raw_listener:
    punch_ports: list[int]
    ws: websockets.WebSocketServerProtocol

    def listen(self):
        print("Client connected. Starting listener...")
        try:
            sniff(lfilter=lambda x: x.haslayer(UDP) and x[UDP].dport == 3658,
                  prn=lambda x: self.send_packet(x))
        except Exception as e:
            print(f"Error in listen: {repr(e)}")
    
    def send_packet(self, pkt):
        try:
            sport = str(pkt[UDP].sport)

            if sport in self.punch_ports:
                return
            
            self.ws.send(sport)
            self.punch_ports.append(sport)
        except Exception as e:
            print(f"Error in send_packet: {repr(e)}")


def main():
    try:
        redirector = Redirector()
        server_thread = threading.Thread(target=redirector.serve, daemon=True)
        server_thread.start()
        while not redirector.websocket:
            pass
        raw_listener = Raw_listener(punch_ports=[], ws=redirector.websocket)
        listener_thread = threading.Thread(target=raw_listener.listen, daemon=True)
        listener_thread.start()

        for thread in [server_thread, listener_thread]:
            thread.join()

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()