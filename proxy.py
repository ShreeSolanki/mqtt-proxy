import threading
import paho.mqtt.client as mqtt
import requests
import json
import os
from flask import Flask

app = Flask(__name__)

MQTT_HOST  = "broker.hivemq.com"
MQTT_PORT  = 1883
MQTT_TOPIC = "meter/data"
WEBHOOK    = "https://app.geoclic-solutions.com/eco-ia/api/webhook"

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected rc={rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload}")
        r = requests.post(WEBHOOK, json=payload, timeout=10)
        print(f"→ {r.status_code} | {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()

# Start MQTT in background thread when Flask starts
t = threading.Thread(target=start_mqtt, daemon=True)
t.start()

@app.route("/")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
