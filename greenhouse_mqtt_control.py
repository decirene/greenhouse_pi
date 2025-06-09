import paho.mqtt.client as mqtt
import ssl
import serial
import json

ENDPOINT = "a1j35o2h3vm5jo-ats.iot.ap-southeast-2.amazonaws.com"
PORT = 8883
TOPIC = "greenhouse/command"

CA_CERT = "AmazonRootCA1.pem"
CERTFILE = "d6acdac29a8b4e92aaa0e3bb61c0ac83442e81f885c9452141f18a0e048c52e5-certificate.pem.crt"
KEYFILE = "d6acdac29a8b4e92aaa0e3bb61c0ac83442e81f885c9452141f18a0e048c52e5-private.pem.key"

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to AWS IoT Core")
        client.subscribe(TOPIC)
    else:
        print("Connection failed:", rc)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Received Command:", payload)

        if "servo" in payload:
            angle = int(payload["servo"])
            command = f"SERVO:{angle}\n"
            ser.write(command.encode())
            print("Sent to Arduino:", command.strip())

        if "led" in payload:
            if payload["led"] == "bright":
                command = "LED:BRIGHT\n"
            else:
                command = "LED:DARK\n"
            ser.write(command.encode())
            print("Sent to Arduino:", command.strip())

    except Exception as e:
        print("Error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(ca_certs=CA_CERT, certfile=CERTFILE, keyfile=KEYFILE, tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect(ENDPOINT, PORT, 60)
client.loop_forever()
