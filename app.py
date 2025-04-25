from flask import Flask, render_template, request
from fetch_ram_data import fetch_ram_data

app = Flask(__name__)

@app.route("/")
@app.route("/<region>")
def home(region="us"):
    data = fetch_ram_data(region=region)
    type_filter = request.args.get("type")
    condition_filter = request.args.get("condition")
    form_filter = request.args.get("form")

    if type_filter:
        data = [p for p in data if p["type"] == type_filter]
    if condition_filter:
        data = [p for p in data if p["condition"] == condition_filter]
    if form_filter:
        data = [p for p in data if p["form_factor"] == form_filter]

    data = sorted(data, key=lambda x: x["price_per_gb"] or 9999)

    return render_template("index.html",
        products=data,
        selected_type=type_filter,
        selected_condition=condition_filter,
        selected_form=form_filter,
        region=region
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

