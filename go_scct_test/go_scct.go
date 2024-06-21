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
    snapshotLen = 1024
    promiscuous = false
    timeout     = 30 * time.Second
    ps2IP      = "192.168.0.166"
    ps2Port    = 1001
    remoteIP   = "100.26.186.59"
    remotePort = 3658
)

func main() {
    device := "en0" // Replace with the correct network interface name from step 1
    handle, err := pcap.OpenLive(device, snapshotLen, promiscuous, timeout)
    if err != nil {
        log.Fatal(err)
    }
    defer handle.Close()

    // Set filter to capture UDP packets originating from ps2IP
    filter := fmt.Sprintf("udp and src host %s and src port %d", ps2IP, ps2Port)
    err = handle.SetBPFFilter(filter)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Listening for UDP packets originating from %s:%d\n", ps2IP, ps2Port)

    remoteAddr := fmt.Sprintf("%s:%d", remoteIP, remotePort)
    remoteUDPAddr, err := net.ResolveUDPAddr("udp", remoteAddr)
    if err != nil {
        log.Fatal(err)
    }

    conn, err := net.DialUDP("udp", nil, remoteUDPAddr)
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
    for packet := range packetSource.Packets() {
        fmt.Println("Captured packet:", packet)

        // Check if packet is the correct length
        if len(packet.Data()) == 70 {
            _, err = conn.Write(packet.Data())
            if err != nil {
                log.Println("Error forwarding UDP packet:", err)
            } else {
                fmt.Printf("Forwarded UDP packet to %s:%d\n", remoteIP, remotePort)
            }
        }
    }
}
