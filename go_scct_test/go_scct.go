package main

import (
    "fmt"
    "log"
    "net"
    "time"

    "github.com/google/gopacket"
    "github.com/google/gopacket/pcap"
)

const (
    device       = "eth0" // Replace with correct network interface name
    snapshotLen  = 1024
    promiscuous  = false
    timeout      = 30 * time.Second
    bufferSize   = 65535
    ps2IP        = "192.168.0.166"
    ps2Port      = 3658
    remoteIP     = "100.26.186.59" 
    remotePort   = 3658                   
)

func main() {
    // Open device for capturing packets
    handle, err := pcap.OpenLive(device, snapshotLen, promiscuous, timeout)
    if err != nil {
        log.Fatal(err)
    }
    defer handle.Close()

    // Set filter to capture UDP packets destined for 192.168.0.166
    filter := fmt.Sprintf("udp and dst host %s and dst port %d", ps2IP, ps2Port)
    err = handle.SetBPFFilter(filter)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Listening for UDP packets destined for %s:%d\n", ps2IP, ps2Port)

    // Prepare connection to forward packets
    remoteAddr := fmt.Sprintf("%s:%d", remoteIP, remotePort)
    remoteUDPAddr, err := net.ResolveUDPAddr("udp", remoteAddr)
    if err != nil {
        log.Fatal(err)
    }

    // Buffer for incoming packets
    buffer := make([]byte, bufferSize)

    // Packet processing loop
    packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
    for packet := range packetSource.Packets() {
        // Extract UDP layer
        udpLayer := packet.Layer(gopacket.LayerTypeUDP)
        if udpLayer == nil {
            continue
        }

        udp, ok := udpLayer.(*gopacket.UDP)
        if !ok {
            continue
        }

        // Check if packet is destined for PS2 console
        if udp.DstPort == layers.UDPPort(ps2Port) && udp.DstIP.String() == ps2IP {
            // Extract payload
            payload := udp.Payload

            // Forward packet to remote destination
            _, err := net.DialUDP("udp", nil, remoteUDPAddr)
            if err != nil {
                log.Println("Error forwarding UDP packet:", err)
                continue
            }

            _, err = conn.WriteToUDP(payload, remoteUDPAddr)
            if err != nil {
                log.Println("Error forwarding UDP packet:", err)
                continue
            }

            fmt.Printf("Forwarded UDP packet to %s:%d\n", remoteIP, remotePort)
        }
    }
}
