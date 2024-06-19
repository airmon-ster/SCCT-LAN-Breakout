# Overview
With the Ubisoft servers being down for Splinter Cell Choas Theory for quite some time, a number of hosted services have cropped up that allow for LAN games to be played over technologies such as VPNs, tunnels, etc.
<br><br>
However, these hosted services have a number of issues that have inspired this simple workaround. Extra cloud processing, encryption, encapsulation, excessive broadcast traffic, and others all add latency to the equation. Not to mention there have been times that these services undergo maintenance and stop play all together.
<br><br>
Having said that, this workout will only work for the PS2 version of SCCT by emulating a server that relies on spoofed UDP packets that redirect the PS2 to the game host's server over the internet.
<br><br>
![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/9b24ebff-cd74-4b12-beb0-9a7f812c29fe)
<br><br>
# Requirements
As seen in the diagram above, there are a few requirements to get this up and running.
<br>
### Host
- Open UDP ports 3658 on their WAN address to allow the players to connect. Forward this port to the PS2's local IP address.
- Configure their PS2 (or PCSX2 Emulator with matching network configuration) with a valid, working IP Address on their local network (As opposed to the XLINK configuration with strange MAC/10.253.0.0/16 configurations)
### Players
- Configure their PS2 (or PCSX2 Emulator with matching network configuration)  with a valid, working IP Address on their local network (As opposed to the XLINK configuration with strange MAC/10.253.0.0/16 configurations)
- Place a *nix based computer on that same network (Windows does not allow sending spoofed source IP addresses as raw sockets)
- Install Python3 and python3-pip on the *nix based computer
- Able to run the scct.py program on the *nix computer on their local network
# Script Installation and Usage
### Install
- Download this repository
- Extract the files
```
cd <SCCT-LAN-Breakout>
sudo apt install python3-pip
python3 -m pip install -r requirements.txt
```
### Run
```
sudo python3 ./scct.py --host <external host's ip address> --bc <your local broadcast address>
```
- Search for LAN Game
- Hopefully when you now search for a game in the LAN menu, you will see the game hosted by SCCTPS2
- Join game and hope that host has the UDP port 3658 forwarded correctly to their PS2's internal IP address
  
![image](https://github.com/airmon-ster/SCCT-LAN-Breakout/assets/31023869/ed9cc908-bb97-4cc4-85e4-9d9aa60f4715)
