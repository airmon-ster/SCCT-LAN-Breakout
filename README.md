# Overview
With the Ubisoft servers being down for Splinter Cell Choas Theory for quite some time, a number of hosted services have cropped up that allow for LAN games to be played over technologies such as VPNs, tunnels, etc.
<br><br>
However, these hosted services have a number of issues that have inspired this simple workaround. Extra cloud processing, encryption, encapsulation, excessive broadcast traffic, and others all add latency to the equation. Not to mention there have been times that these services undergo maintenance and stop play all together.
<br><br>
Having said that, this workout will only work for the PS2 version of SCCT by emulating a server that relies on spoofed UDP packets that redirect the PS2 to the game host's server over the internet.
<br><br>
## Via Port Forwarding (100% Success rate)
- Note: Not all ISPs allow incomming traffic to be routed to home IP Addresses. Carrier Grade NAT or other measures may be in place.

![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/c12369bd-9a68-4d53-87ab-636e6fe48af7)

## Via Firewall Hole Punching V2 (Alpha Testing Phase)
- Note: Hosts that have a router that randomize the source ports post NAT will not be able to host using this method.
- Note: Signal_Server must block the hole-punch UDP packets so that they do not end up hitting any of the clients. If they do, hardware ps2s will freeze
  ![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/8503049a-28a4-4762-a01f-896584b1d7a9)

## Via Firewall Hole Punching V1 (Pre-Alpha Testing Phase) - Removed
- Note: Some routers rewrite the source port as it leaves their NAT. For routers that do this, the player will be unable to join as the ports need to be predicted accurately by the host. Either configure your router to use static source ports during NAT, or provision a cloud redirector (out of the scope of this repo for now).
<br><br>This is usually seen when others can join the host, but you still see a "Game no longer available screen." Ensure you are using the correct IP address and then troubleshoot.
![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/b6f70a6a-ac6f-481c-a634-0cb61711ba16)
## Via UPnP (Untested)
- Note: This method is untested and may not work at all since some UPnP servers do not allow IPs other than the intended destination to make a UPnP request.
  ![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/dfe662c6-fbc2-4f96-b9f3-50cea13a9b4a)
<br><br>
# Requirements
As seen in the diagram above, there are a few requirements to get this up and running.
<br>
### Host
- Open UDP ports 3658 on their WAN address to allow the players to connect. Forward this port to the PS2's local IP address.
- Configure their PS2 (or PCSX2 Emulator with matching network configuration) with a valid, working IP Address on their local network (As opposed to the XLINK configuration with MAC/10.253.0.0/16 configurations)
### Players
- Configure their PS2 (or PCSX2 Emulator with matching network configuration)  with a valid, working IP Address on their local network (As opposed to the XLINK configuration with MAC/10.253.0.0/16 configurations)
- Place computer on that same network
- Install Python3 and python3-pip
- Able to run the scct.py program on their local network
# Script Installation and Usage
### Install (Linux/Mac)
- Download this repository
- Extract the files
```
cd <SCCT-LAN-Breakout>
sudo apt install python3-pip
python3 -m pip install -r requirements.txt
```
### Install (Windows)
- Download the latest version from Releases (Right column on this page)
- Run the bat file
### Server Run
```
sudo python ./scct.py --help
sudo python ./scct.py server --ps <your ps2's private ip address> --signal testserver.scct.airmon-ster.com [--upnp]
```
### Client Run
```
sudo python ./scct.py --help
sudo python3 ./scct.py client --remote <external host's ip address> --broadcast <your local broadcast address>
```
- Search for LAN Game
- Hopefully when you now search for a game in the LAN menu, you will see the game hosted by SCCTPS2
- Join game and hope that host has the UDP port 3658 forwarded correctly to their PS2's internal IP address
  
![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/c67af4b4-6001-46c5-925c-ac269feeda86)

### Test
Test server is currently up at testserver.scct.airmon-ster.com. Later efforts will auto-healthcheck this and report appropriately.
