from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is working!"

@app.route("/get-inventory")
def get_inventory():
    return jsonify([
        {"name": "Beaker", "image_url": "https://example.com/beaker.jpg"},
        {"name": "Microscope", "image_url": "https://example.com/microscope.jpg"}
    ])

@app.route("/add-item", methods=["POST"])
def add_item():
    data = request.json
    return jsonify({"status": "received", "item": data})

# Add this part to run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)