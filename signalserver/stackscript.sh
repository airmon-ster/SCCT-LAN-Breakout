#!/bin/bash
#<UDF name="host" label="game host ip">
# HOST=
apt-get update && apt-get upgrade -y
apt install git python3-pip python3.12-venv -y
git clone https://github.com/airmon-ster/SCCT-LAN-Breakout.git
cd SCCT-LAN-Breakout/signalserver
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r requirements.txt
cp scct.service /etc/systemd/system/
systemctl enable scct
sysctl net.ipv4.ip_forward=1
iptables -t nat -A PREROUTING -p udp --dport 3658 -j DNAT --to-destination $HOST
iptables -t nat -A POSTROUTING -p udp --dport 3658 -j MASQUERADE
iptables -t raw -A PREROUTING -p udp --sport 3658 -m length --length 1100:1300 -j DROP