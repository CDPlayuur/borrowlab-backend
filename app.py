from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize the Flask app and SQLAlchemy
app = Flask(__name__)
CORS(app)  # Allow all domains (for testing)

# Configure the PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kdbiPtzehPaslyshovEgqYgfPrMABLfy@postgres.railway.internal:5432/railway'  # Replace with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)
CORS(app, origins=["http://borrowlabmaterials.ct.ws"])
# Define the InventoryItem model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    amount_in_stock = db.Column(db.Integer, nullable=False, default=0)
    consumable = db.Column(db.Boolean, nullable=False, default=False)
    short_description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<InventoryItem {self.name}>'

# Route to get inventory from the database
@app.route("/get-inventory")
def get_inventory():
    items = InventoryItem.query.all()  # Get all items from the database
    return jsonify([{
        "id": item.id,
        "name": item.name,
        "image_url": item.image_url,
        "amount_in_stock": item.amount_in_stock,
        "consumable": item.consumable,
        "short_description": item.short_description
    } for item in items])

# Add this part to run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
