import paho.mqtt.client as mqtt
import requests
import json
import os

MQTT_HOST   = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "meter/data"
WEBHOOK     = "https://app.geoclic-solutions.com/eco-ia/api/webhook"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker, rc={rc}")
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload}")
        r = requests.post(WEBHOOK, json=payload, timeout=10)
        print(f"→ {r.status_code} | {r.text}")
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_forever()
