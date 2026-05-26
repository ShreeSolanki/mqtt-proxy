from flask import Flask, request
import requests, os

app = Flask(__name__)
WEBHOOK = "https://app.geoclic-solutions.com/eco-ia/api/webhook"

@app.route("/forward", methods=["POST"])
def forward():
    data = request.get_json(force=True)
    r = requests.post(WEBHOOK, json=data, timeout=10)
    print(f"→ {r.status_code} | {r.text}")
    return str(r.status_code), r.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
