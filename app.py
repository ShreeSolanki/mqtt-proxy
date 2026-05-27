import threading
import time
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
SELF_URL   = "https://mqtt-proxy-v0bs.onrender.com/"

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected rc={rc}", flush=True)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        d = json.loads(msg.payload.decode())
        print(f"Received: {d}", flush=True)

        payload = {
            "id":                    "ENERS02A",
            "ID":                    "ENERS02A",
            "IMEI":                  d.get("imei",  "UNKNOWN"),
            "Voltage_B":             d.get("vb",    0.0),
            "Voltage_Phase_Neutral": d.get("vpn",   0.0),
            "Voltage_Phase_Phase":   d.get("vry",   0.0),
            "Frequency_Hz":          d.get("freq",  0.0),
            "Current_R":             d.get("ir",    0.0),
            "Current_Y":             d.get("iy",    0.0),
            "Current_B":             d.get("ib",    0.0),
            "Current_Average":       d.get("i_avg", 0.0),
            "Total_Power_W":         d.get("ptot",  0.0),
            "Energy_kWh":            d.get("kwhr",  0.0),
            "Timestamp":             d.get("ts",    0),
            "Socket Allowed":        True
        }

        print(f"Forwarding: {payload}", flush=True)
        r = requests.post(WEBHOOK, json=payload, timeout=10)
        print(f"→ {r.status_code} | {r.text[:500]}", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)

def start_mqtt():
    while True:
        try:
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as e:
            print(f"MQTT error, reconnecting in 5s: {e}", flush=True)
            time.sleep(5)

def keep_alive():
    while True:
        time.sleep(840)  # every 14 minutes
        try:
            requests.get(SELF_URL, timeout=5)
            print("Keep-alive ping sent", flush=True)
        except Exception as e:
            print(f"Keep-alive failed: {e}", flush=True)

threading.Thread(target=start_mqtt, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

@app.route("/")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
