package main

import (
	"fmt"
	"net"
	"os"
)

func main() {
	// Local IP and port for the PS2 on your LAN
	localIP := "192.168.0.166"
	localPort := 3658

	// Remote IP and port (example for another PS2 on a different LAN)
	remoteIP := "100.26.186.59"
	remotePort := 3658

	// Start UDP listener on the local IP and port
	localAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf("%s:%d", localIP, localPort))
	if err != nil {
		fmt.Println("Error resolving local address:", err)
		os.Exit(1)
	}

	conn, err := net.ListenUDP("udp", localAddr)
	if err != nil {
		fmt.Println("Error listening:", err)
		os.Exit(1)
	}
	defer conn.Close()

	fmt.Printf("Listening on %s:%d\n", localIP, localPort)

	// Create a buffer for incoming data
	buffer := make([]byte, 1024)

	for {
		// Read UDP packet from PS2
		n, addr, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading:", err)
			continue
		}

		fmt.Printf("Received UDP packet from %s:%d\n", addr.IP.String(), addr.Port)

		// Simulate sending the packet to the remote PS2
		remoteAddr := &net.UDPAddr{
			IP:   net.ParseIP(remoteIP),
			Port: remotePort,
		}

		_, err = conn.WriteToUDP(buffer[:n], remoteAddr)
		if err != nil {
			fmt.Println("Error writing to remote:", err)
			continue
		}

		fmt.Printf("Sent UDP packet to %s:%d\n", remoteIP, remotePort)
	}
}
