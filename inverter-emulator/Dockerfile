# inverter-emulator/Dockerfile
FROM python:3.8-slim

LABEL maintainer="Ammar Khan <ammar.khan@adelaide.edu.au>"

# 1) Install system packages: mosquitto (MQTT broker), supervisor, and SSL libs
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      mosquitto \
      mosquitto-clients \
      libssl-dev \
      wget \
      supervisor \
      && rm -rf /var/lib/apt/lists/*

# 2) Copy Python dependencies list and install them
COPY requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app
RUN pip3 install --no-cache-dir -r requirements.txt

# 3) Copy emulator scripts and configs
COPY mppt_simulator.py /usr/src/app/mppt_simulator.py
COPY flask_api.py /usr/src/app/flask_api.py
COPY mosquitto.conf /usr/src/app/mosquitto.conf
COPY mosquitto_passwd /usr/src/app/mosquitto_passwd
COPY certs/ /usr/src/app/certs/
COPY supervisord.conf /usr/src/app/supervisord.conf

# 4) Ensure certificates are secure
RUN chmod 600 /usr/src/app/certs/*

# 5) Expose MQTT plaintext (1883), MQTT+TLS (8883), Modbus (502), Flask API (5000)
EXPOSE 1883 8883 502 5000

# 6) Launch supervisor to manage broker, API, and simulator
CMD ["supervisord", "-n", "-c", "/usr/src/app/supervisord.conf"]
