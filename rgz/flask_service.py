from flask import Flask, request, jsonify

app = Flask(__name__)

RATES = {
    "USD": 100.01,
    "EUR": 108.56
}

@app.route("/rate")
def get_rate():
    currency = request.args.get("currency")
    if currency not in RATES:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400
    return jsonify({"rate": RATES[currency]}), 200

if __name__ == "__main__":
    app.run(port=8000)
