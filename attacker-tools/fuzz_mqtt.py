
# attacker-tools/fuzz_mqtt.py

from scapy.all import IP, TCP, Raw, sr1
import random
import time

BROKER_IP = "10.0.2.15"
BROKER_PORT = 1883

def fuzz_mqtt_connect():
    packet_type = 0x10
    flags = 0x00
    fixed_header = bytes([packet_type | flags, 0x00])

    protocol_name = b"MQIsdp"
    proto_len = random.choice([0, 1, 2, len(protocol_name) + 5])
    variable_header = proto_len.to_bytes(2, byteorder="big") + protocol_name

    proto_level = random.randint(0, 255)
    connect_flags = random.randint(0, 255)
    keepalive = random.randint(0, 1024)

    payload = b""
    pkt = IP(dst=BROKER_IP) / TCP(dport=BROKER_PORT, flags="PA") / Raw(load=fixed_header
                                                                       + variable_header
                                                                       + bytes([proto_level, connect_flags]) 
                                                                       + keepalive.to_bytes(2, byteorder="big")
                                                                       + payload)
    return pkt

def send_fuzz(rounds=50, delay=0.5):
    for i in range(rounds):
        pkt = fuzz_mqtt_connect()
        resp = sr1(pkt, timeout=1, verbose=0)
        print(f"[{i+1}] Sent malformed CONNECT. Response: {resp.summary() if resp else 'No response'}")
        time.sleep(delay)

if __name__ == "__main__":
    send_fuzz()


