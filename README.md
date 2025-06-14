# Solar Inverter Security Testbed

A fully containerized, end-to-end security testbed for an IoT-enabled solar inverter.
Emulates an inverter’s MPPT/Modbus interfaces and MQTT telemetry, a SCADA stack for data collection and visualization, and a suite of attacker tools for vulnerability assessment, fuzzing, and MITM.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Directory Structure](#directory-structure)
6. [Components & Usage](#components--usage)

   * [Inverter Emulator](#1-inverter-emulator)
   * [SCADA Stack](#2-scada-stack)
   * [Attacker Tools](#3-attacker-tools)
7. [Example Workflows](#example-workflows)

---

## Overview

This repository provides:

* **Inverter Emulator** – A Docker container simulating an MPPT-based solar inverter with:

  * **Modbus/TCP** endpoint (port 502) for register reads/writes
  * **MQTT** telemetry (port 1883 plaintext & 8883 TLS)
  * **HTTPS REST API** (port 5000) for configuration & firmware uploads

* **SCADA Stack** – Docker-Compose services:

  * **InfluxDB** (time-series database)
  * **Grafana** (dashboard & alerting)
  * **Node-RED** (data ingestion flow)

* **Attacker Tools** – Scripts for security testing:

  * `nmap_scan.sh` – port & version enumeration
  * `fuzz_mqtt.py` – malformed MQTT CONNECT fuzzing (via Scapy)
  * `fuzz_modbus.py` – random Modbus function-code fuzzing
  * `mitm_mqtt.sh` – ARP-spoof + Wireshark capture of MQTT traffic

Use this testbed to demonstrate and measure:

* **Confidentiality** leaks (plaintext MQTT/Modbus)
* **Integrity** attacks (fuzzing, malformed packets)
* **Availability** disruption potential
* **Authentication & Encryption** efficacy

---

## Architecture

```
┌────────────────────────┐
│     Host Ubuntu 22.04  │
│  (VirtualBox / UTM VM) │
│                        │
│ ┌────────────────────┐ │
│ │ Inverter Emulator  │ │
│ │  • Mosquitto (1883,8883)      │
│ │  • MPPT Simulator (502)       │
│ │  • Flask API (5000)           │
│ └────────────────────┘ │
│                        │
│ ┌────────────────────┐ │
│ │   SCADA Stack      │ │
│ │  • InfluxDB (8086)           │
│ │  • Grafana (3000)            │
│ │  • Node-RED (1880)           │
│ └────────────────────┘ │
│                        │
│ ┌────────────────────┐ │
│ │  Attacker Tools    │ │
│ │  Scripts on Host   │ │
│ └────────────────────┘ │
└────────────────────────┘
```

---

## Prerequisites

* **Host OS**: Ubuntu 22.04 LTS (or any Linux with Docker & Python 3.8+)
* **Docker** & **docker-compose** (or Docker Compose V2 plugin)
* **Python 3** & **virtualenv** (for attacker tools)
* Utilities: `mosquitto-clients`, `nmap`, `dsniff`, `wireshark`, `xterm`

---

## Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-org/solar-inverter-security.git
   cd solar-inverter-security
   ```

2. **Start the Inverter Emulator**

   ```bash
   cd inverter-emulator
   docker build -t inverter-emulator:latest .
   docker run -d \
     --name inverter_emulator \
     -p 1883:1883 \
     -p 8883:8883 \
     -p 502:502 \
     -p 5000:5000 \
     inverter-emulator:latest
   ```

3. **Initialize SCADA Stack**

   ```bash
   cd ../scada-server
   # bring up InfluxDB and create database
   docker compose up -d influxdb
   sleep 10
   docker exec -it influxdb influx -execute "CREATE DATABASE inverter_db"
   docker compose down

   # start all SCADA services
   docker compose up -d
   ```

4. **Access Interfaces**

   * Grafana → [http://localhost:3000](http://localhost:3000) (admin/admin)
   * Node-RED → [http://localhost:1880](http://localhost:1880) (flow imports in `/node-red/flows.json`)
   * MQTT plaintext → port 1883
   * MQTT TLS/auth → port 8883 (user: `mqtt_user` / pass: `mqtt_pass`)
   * Modbus/TCP → port 502
   * REST API → [https://localhost:5000](https://localhost:5000) (basic auth: `admin:admin123`)

5. **Run Attacker Tools**

   ```bash
   cd ../attacker-tools
   bash nmap_scan.sh <INVERTER_IP> <GATEWAY_IP> <INTERFACE>
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt  # paho-mqtt, pymodbus, scapy
   # fuzzing
   sudo .venv/bin/python3 fuzz_mqtt.py
   python3 fuzz_modbus.py
   sudo bash mitm_mqtt.sh <INVERTER_IP> <GATEWAY_IP> <INTERFACE>
   ```

---

## Directory Structure

```
solar-inverter-security/
├── inverter-emulator/       # Dockerfile & emulator code
│   ├── Dockerfile
│   ├── mosquitto.conf
│   ├── supervisord.conf
│   ├── mppt_simulator.py
│   ├── flask_api.py
│   └── certs/               # TLS certificates & passwords
├── scada-server/            # docker-compose for InfluxDB, Grafana, Node-RED
│   ├── docker-compose.yml
│   ├── influxdb/
│   ├── grafana/
│   └── node-red/
│       └── flows.json       # Node-RED flow to ingest MQTT → InfluxDB
└── attacker-tools/          # Security test scripts
    ├── nmap_scan.sh
    ├── fuzz_mqtt.py
    ├── fuzz_modbus.py
    └── mitm_mqtt.sh
```

---

## Components & Usage

### 1. Inverter Emulator

* **MQTT broker**: Mosquitto with TLS (`8883`) & plaintext (`1883`)
* **MPPT sim**: Publishes JSON telemetry & hosts Modbus on `502`
* **Flask API**:

  * `GET /api/health`
  * `GET/POST /api/config` (role-based)
  * `POST /api/firmware` (admin only)

### 2. SCADA Stack

* **InfluxDB** stores measurement `inverter_data`
* **Node-RED** subscribes to MQTT and writes to InfluxDB
* **Grafana** dashboards visualize voltage/current/power over time

### 3. Attacker Tools

* **nmap\_scan.sh**
* **fuzz\_mqtt.py** (Scapy)
* **fuzz\_modbus.py** (PyModbus)
* **mitm\_mqtt.sh** (ARP spoof + Wireshark)

---

## Example Workflows

1. **Baseline Reconnaissance**

   ```bash
   # discover open ports
   ./nmap_scan.sh 10.0.2.15 10.0.2.1 ens33

   # view plaintext telemetry
   mosquitto_sub -h 10.0.2.15 -p 1883 -t inverter/INV001/telemetry -v

   # read Modbus register
   python3 - <<EOF
   from pymodbus.client import ModbusTcpClient
   c=ModbusTcpClient("10.0.2.15",502)
   if c.connect():
       print(c.read_holding_registers(address=0,count=1,slave=1))
       c.close()
   EOF
   ```

2. **Enable TLS/Auth & Re-test**

   ```bash
   mosquitto_sub --cafile ../inverter-emulator/certs/broker.crt \
     -h 10.0.2.15 -p 8883 -t inverter/INV001/telemetry \
     -u mqtt_user -P mqtt_pass -v
   ```

3. **Fuzzing & MITM**

   ```bash
   sudo .venv/bin/python3 fuzz_mqtt.py
   python3 fuzz_modbus.py
   sudo bash mitm_mqtt.sh 10.0.2.15 10.0.2.1 ens33
   ```

---

