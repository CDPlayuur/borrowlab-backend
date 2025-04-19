from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json

# Initialize the Flask app and SQLAlchemy
app = Flask(__name__)
CORS(app)  # Allow all domains (for testing)

# Configure the PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kdbiPtzehPaslyshovEgqYgfPrMABLfy@postgres.railway.internal:5432/railway'
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

# NEW: Define the PendingRequest model
class PendingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    professor = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string of selected items

# Route to get inventory from the database
@app.route("/get-inventory")
def get_inventory():
    items = InventoryItem.query.all()
    return jsonify([{
        "id": item.id,
        "name": item.name,
        "image_url": item.image_url,
        "amount_in_stock": item.amount_in_stock,
        "consumable": item.consumable,
        "short_description": item.short_description
    } for item in items])

# NEW: Route to receive student request and save to database
@app.route("/submit-request", methods=["POST"])
def submit_request():
    data = request.get_json()
    student_name = data.get("student_name")
    student_id = data.get("student_id")
    professor = data.get("professor")
    subject = data.get("subject")
    items = data.get("items")  # this should be a list

    if not all([student_name, student_id, professor, subject, items]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    request_record = PendingRequest(
        student_name=student_name,
        student_id=student_id,
        professor=professor,
        subject=subject,
        items=json.dumps(items)  # convert list to string for storage
    )

    db.session.add(request_record)
    db.session.commit()

    return jsonify({"success": True, "message": "Request submitted successfully"})

# Add this part to run the server
if __name__ == "__main__":
    with app.app_context():  # NEW: make sure tables are created
        db.create_all()

    app.run(host="0.0.0.0", port=8000)
