import time
import sqlite3
import json
import ssl
import requests
import paho.mqtt.client as mqtt

# AWS IoT MQTT 
MQTT_ENDPOINT = "a1j35o2h3vm5jo-ats.iot.ap-southeast-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "greenhouse/command"

CA_CERT = "AmazonRootCA1.pem"
CERTFILE = "d6acdac29a8b4e92aaa0e3bb61c0ac83442e81f885c9452141f18a0e048c52e5-certificate.pem.crt"
KEYFILE = "d6acdac29a8b4e92aaa0e3bb61c0ac83442e81f885c9452141f18a0e048c52e5-private.pem.key"

# API(WeatherAPI.com)
WEATHER_API_KEY = "ab2e0251fdba4544a8c152210250406" 
LOCATION = "Kuala Lumpur"

def get_latest_data():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, light FROM sensor_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "temperature": row[1],
            "light": row[2]
        }
    return None


def get_weather_condition():
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={LOCATION}&aqi=no"
        res = requests.get(url)
        weather = res.json()
        condition = weather['current']['condition']['text']
        print("Current weather:", condition)
        return condition
    except Exception as e:
        print("Weather API failed:", e)
        return "Unknown"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to AWS IoT Core")
    else:
        print("Failed to connect:", rc)

client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ca_certs=CA_CERT, certfile=CERTFILE, keyfile=KEYFILE, tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect(MQTT_ENDPOINT, MQTT_PORT, 60)
client.loop_start()

try:
    while True:
        data = get_latest_data()
        if data:
            condition = get_weather_condition()
            print(f"Temp: {data['temperature']} *C, Light: {data['light']} lux")

            command = {}

            if data["temperature"] > 25 or "Sunny" in condition:
                command["servo"] = 90
            else:
                command["servo"] = 0

            if data["light"] > 850:
                command["led"] = "bright"
            else:
                command["led"] = "dark"

            client.publish(MQTT_TOPIC, json.dumps(command))
            print("Sent Command:", command)

        time.sleep(15)

except KeyboardInterrupt:
    print("Automation stopped.")
finally:
    client.loop_stop()
    client.disconnect()
