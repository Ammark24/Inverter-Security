# inverter-emulator/mppt_simulator.py

import time
import random
import threading
import json
from paho.mqtt import client as mqtt_client
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSequentialDataBlock

# Configuration
INVERTER_ID = "INV001"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_TELEMETRY = f"inverter/{INVERTER_ID}/telemetry"
MQTT_TOPIC_CONTROL = f"inverter/{INVERTER_ID}/control"
MODBUS_PORT = 502

# State variables
current_voltage = 0.0
current_current = 0.0
current_power = 0.0
shutdown_flag = False

# Initialize Modbus datastore (single slave with ID=1)
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [0]*100),
    ir=ModbusSequentialDataBlock(0, [0]*100)
)
context = ModbusServerContext(slaves=store, single=True)

def run_modbus_server():
    """Start a Modbus/TCP server on port 502."""
    StartTcpServer(context, address=("0.0.0.0", MODBUS_PORT))

def simulate_mppt(mqtt_client):
    """Every second, publish synthetic telemetry over MQTT."""
    global current_voltage, current_current, current_power, shutdown_flag

    while True:
        if shutdown_flag:
            current_voltage = 0.0
            current_current = 0.0
            current_power = 0.0
        else:
            current_voltage = round(random.uniform(300.0, 400.0), 2)   # DC bus voltage
            current_current = round(random.uniform(5.0, 10.0), 2)      # amperes
            current_power = round(current_voltage * current_current, 2)

        telemetry = {
            "inverter_id": INVERTER_ID,
            "voltage": current_voltage,
            "current": current_current,
            "power": current_power,
            "timestamp": int(time.time())
        }
        mqtt_client.publish(MQTT_TOPIC_TELEMETRY, json.dumps(telemetry), qos=1)
        time.sleep(1)

def on_control_message(client, userdata, msg):
    """Handle control commands (shutdown, start, reset) arriving via MQTT."""
    global shutdown_flag
    try:
        payload = json.loads(msg.payload.decode())
        cmd = payload.get("command", "").lower()
        if cmd == "shutdown":
            shutdown_flag = True
        elif cmd in ("start", "reset"):
            shutdown_flag = False
        print(f"[MPPT] Received control command: {cmd}")
    except Exception as e:
        print(f"[MPPT] Invalid control message: {e}")

def main():
    # 1) Connect to Mosquitto broker (plaintext). If you enable TLS, adjust below.
    client = mqtt_client.Client(f"emulator-{INVERTER_ID}")
    client.username_pw_set(username="mqtt_user", password="mqtt_pass")
    client.on_message = on_control_message
    client.connect(host=MQTT_BROKER, port=MQTT_PORT, keepalive=60)

    # 2) Subscribe to control topic
    client.subscribe(MQTT_TOPIC_CONTROL, qos=1)
    client.loop_start()

    # 3) Start Modbus server in a separate thread
    modbus_thread = threading.Thread(target=run_modbus_server, daemon=True)
    modbus_thread.start()

    # 4) Start publishing telemetry
    simulate_mppt(client)

if __name__ == "__main__":
    main()
