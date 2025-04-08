from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)
USDA_API_KEY = "P2HbOqH02UEVpFKWZic4od23qfkFroTM7iPIDMkb"

@app.route("/nutrients", methods=["GET"])
def get_nutrients():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    search_params = {"query": query, "api_key": USDA_API_KEY, "pageSize": 1}
    search_resp = requests.get(search_url, params=search_params).json()

    if not search_resp.get("foods"):
        return jsonify({"error": "No food found"}), 404

    fdc_id = search_resp["foods"][0]["fdcId"]
    detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={USDA_API_KEY}"
    detail_resp = requests.get(detail_url).json()

    nutrients_data = []
    for item in detail_resp.get("foodNutrients", [])[:10]:
        nutrient_name = item.get("nutrient", {}).get("name")
        value = item.get("amount")
        unit = item.get("nutrient", {}).get("unitName")
        if nutrient_name and value is not None and unit:
            nutrients_data.append({"name": nutrient_name, "value": value, "unit": unit})

    return jsonify({"food": query, "nutrients": nutrients_data})

@app.route("/.well-known/ai-plugin.json")
def serve_plugin():
    return send_from_directory(".well-known", "ai-plugin.json", mimetype="application/json")

@app.route("/openapi.yaml")
def serve_openapi():
    return send_from_directory(".", "openapi.yaml", mimetype="text/yaml")

@app.route("/logo.png")
def serve_logo():
    return '', 204

@app.route("/legal")
def serve_legal():
    return 'No legal info.', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



