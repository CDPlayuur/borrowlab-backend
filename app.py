from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS
CORS(app)  # Allow all domains (for testing)

# Initialize the Flask app and SQLAlchemy
app = Flask(__name__)

# Configure the PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kdbiPtzehPaslyshovEgqYgfPrMABLfy@postgres.railway.internal:5432/railway'  # Replace with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the InventoryItem model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<InventoryItem {self.name}>'

# Route for home
@app.route("/")
def home():
    return "Backend is working!"

# Route to get inventory from the database
@app.route("/get-inventory")
def get_inventory():
    items = InventoryItem.query.all()  # Get all items from the database
    return jsonify([{"name": item.name, "image_url": item.image_url} for item in items])

# Route to add an item to the database
@app.route("/add-item", methods=["POST"])
def add_item():
    data = request.json
    new_item = InventoryItem(name=data['name'], image_url=data['image_url'])
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"status": "received", "item": {"name": new_item.name, "image_url": new_item.image_url}})

# Add this part to run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
