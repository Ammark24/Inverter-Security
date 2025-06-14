#!/usr/bin/env python3
# attacker-tools/fuzz_modbus.py

from pymodbus.client.sync import ModbusTcpClient
import random
import time

BROKER_IP = "10.0.2.15"  # your inverter emulator IP
BROKER_PORT = 502

def fuzz_modbus(rounds=50, delay=0.5):
    client = ModbusTcpClient(BROKER_IP, port=BROKER_PORT)
    if not client.connect():
        print("Failed to connect to Modbus server.")
        return

    for i in range(rounds):
        func_code = random.choice([1, 2, 3, 4, 5, 6, 15, 16])
        address = random.randint(0, 10)
        count = random.randint(1, 5)
        try:
            if func_code == 1:
                rr = client.read_coils(address, count)
            elif func_code == 2:
                rr = client.read_discrete_inputs(address, count)
            elif func_code == 3:
                rr = client.read_holding_registers(address, count)
            elif func_code == 4:
                rr = client.read_input_registers(address, count)
            elif func_code == 5:
                rr = client.write_coil(address, random.choice([True, False]))
            elif func_code == 6:
                rr = client.write_register(address, random.randint(0, 100))
            elif func_code == 15:
                rr = client.write_coils(
                    address,
                    [random.choice([True, False]) for _ in range(count)]
                )
            elif func_code == 16:
                rr = client.write_registers(
                    address,
                    [random.randint(0, 100) for _ in range(count)]
                )
            else:
                rr = None

            print(f"[{i+1}] Func {func_code:02X} @ {address}, "
                  f"count={count}, response={rr}")
        except Exception as e:
            print(f"[{i+1}] Exception during fuzz: {e}")

        time.sleep(delay)

    client.close()

if __name__ == "__main__":
    fuzz_modbus()
