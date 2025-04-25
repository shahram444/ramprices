from flask import Flask, render_template, request
import json

app = Flask(__name__)

def get_data():
    with open("cache/dummy_data.json", "r") as f:
        return json.load(f)

@app.route("/")
def index():
    data = get_data()
    filters = request.args
    for key, val in filters.items():
        if val:
            data = [d for d in data if str(d.get(key, "")).lower() == val.lower()]
    return render_template("index.html", products=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
