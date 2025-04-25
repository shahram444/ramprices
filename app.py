from flask import Flask, render_template, request
import json
import os
from fetch_ram_data import fetch_ram_data

app = Flask(__name__)

@app.route("/")
@app.route("/<region>")
def home(region="us"):
    try:
        data = fetch_ram_data(region=region)
    except:
        with open("cache/dummy_data.json", "r") as f:
            data = json.load(f)

    # Get filter inputs
    filters = request.args
    type_filter = filters.get("type")
    condition_filter = filters.get("condition")
    form_filter = filters.get("form")

    # Apply filters
    if type_filter:
        data = [p for p in data if p.get("type", "").lower() == type_filter.lower()]
    if condition_filter:
        data = [p for p in data if p.get("condition", "").lower() == condition_filter.lower()]
    if form_filter:
        data = [p for p in data if p.get("form_factor", "").lower() == form_filter.lower()]

    # Sort by price_per_gb if available
    data = sorted(data, key=lambda x: x.get("price_per_gb") or 9999)

    return render_template("index.html",
        products=data,
        selected_type=type_filter,
        selected_condition=condition_filter,
        selected_form=form_filter,
        region=region
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
