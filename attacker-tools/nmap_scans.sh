#!/bin/bash
# attacker-tools/nmap_scan.sh

TARGET_IP="10.0.2.15"  # your Ubuntu VM

echo "Performing version detection scan on $TARGET_IP..."
nmap -sV -p 1883,8883,502,5000 --open $TARGET_IP

echo
echo "Complete port scan (1-1000) on $TARGET_IP..."
nmap -p 1-1000 --open $TARGET_IP
