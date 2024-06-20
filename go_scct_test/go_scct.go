package main

import (
    "fmt"
    "log"
    "net"
    "time"

    "github.com/google/gopacket"
    "github.com/google/gopacket/pcap"
    "github.com/google/gopacket/layers"
)

const (
    device     = "en0" // Replace with correct network interface name
    snapshotLen = 1024
    promiscuous = false
    timeout     = 30 * time.Second
    ps2IP      = "192.168.0.166"
    ps2Port    = 3658
    remoteIP   = "100.26.186.59"
    remotePort = 3658
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

    // Packet processing loop
    packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
    for packet := range packetSource.Packets() {
        // Parse packet layers
        parser := gopacket.NewDecodingLayerParser(
            layers.LayerTypeEthernet,
            &layers.IPv4{},
            &layers.UDP{},
            gopacket.PayloadLayer,
        )

        foundLayerTypes := []gopacket.LayerType{}
        err := parser.DecodeLayers(packet.Data(), &foundLayerTypes)
        if err != nil {
            log.Println("Error decoding layers:", err)
            continue
        }

        var udp *layers.UDP
        var payload []byte

        for _, layerType := range foundLayerTypes {
            if layerType == layers.LayerTypeUDP {
                udp = parser.Layer(layerType).(*layers.UDP)
            } else if layerType == gopacket.LayerTypePayload {
                payload = parser.Layer(layerType).Payload()
            }
        }

        if udp == nil {
            log.Println("UDP layer not found in packet")
            continue
        }

        // Check if packet is destined for PS2 console
        if udp.DstPort == layers.UDPPort(ps2Port) && udp.DstIP.String() == ps2IP {
            // Forward packet to remote destination
            conn, err := net.DialUDP("udp", nil, remoteUDPAddr)
            if err != nil {
                log.Println("Error opening UDP connection:", err)
                continue
            }
            defer conn.Close()

            _, err = conn.Write(payload)
            if err != nil {
                log.Println("Error forwarding UDP packet:", err)
                continue
            }

            fmt.Printf("Forwarded UDP packet to %s:%d\n", remoteIP, remotePort)
        }
    }
}
