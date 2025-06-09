import time
import sqlite3
import json
import ssl
import paho.mqtt.client as mqtt

# AWS IoT Core MQTT endpoint
MQTT_ENDPOINT = "a1j35o2h3vm5jo-ats.iot.ap-southeast-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "greenhouse/data"

# Paths to certificate files
CA_CERT = "AmazonRootCA1.pem"
DEVICE_CERT = "d6acdac29a8b4e92aaa0e3bb61c0ac83442e81f885c9452141f18a0e048c52e5-certificate.pem.crt"
PRIVATE_KEY = "d6acdac29a8b4e92aaa0e3bb61c0ac83442e81f885c9452141f18a0e048c52e5-private.pem.key"

def get_latest_data():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, light, rain_detected FROM sensor_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "timestamp": row[0],
            "temperature": row[1],
            "light": row[2],
            "rain": bool(row[3])
        }
    return None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to AWS IoT Core")
    else:
        print(f"Failed to connect, return code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

# Configure TLS/SSL
client.tls_set(ca_certs=CA_CERT,
               certfile=DEVICE_CERT,
               keyfile=PRIVATE_KEY,
               tls_version=ssl.PROTOCOL_TLSv1_2)

client.connect(MQTT_ENDPOINT, MQTT_PORT, 60)

try:
    client.loop_start()
    while True:
        data = get_latest_data()
        if data:
            client.publish(MQTT_TOPIC, json.dumps(data))
            print("Uploaded to AWS IoT:", data)
        time.sleep(10)
except KeyboardInterrupt:
    print(" MQTT upload stopped.")
finally:
    client.loop_stop()
    client.disconnect()

