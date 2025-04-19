from datetime import datetime
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
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    item_img = db.Column(db.String(255), nullable=True)
    item_stock = db.Column(db.Integer, nullable=False, default=0)
    item_is_consumable = db.Column(db.Boolean, nullable=False, default=False)
    item_desc = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<InventoryItem {self.name}>'

# NEW: Define the PendingRequest model
class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'

    pending_request_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.item_id'), nullable=False)
    student_id = db.Column(db.Text, nullable=False)
    student_name = db.Column(db.Text, nullable=False)
    course = db.Column(db.Text, nullable=False)
    section = db.Column(db.Text, nullable=False)
    prof_name = db.Column(db.Text, nullable=False)
    program = db.Column(db.Text, nullable=False)
    date_filed = db.Column(db.Date, nullable=False)
    date_needed = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')


# Route to get inventory from the database
@app.route("/get-inventory")
def get_inventory():
    items = InventoryItem.query.all()
    return jsonify([{
        "id": item.item_id,
        "name": item.item_name,
        "image_url": item.item_img,
        "amount_in_stock": item.item_stock,
        "consumable": item.item_is_consumable,
        "short_description": item.item_desc
    } for item in items])

@app.route("/submit-request", methods=["POST"])
def submit_request():
    data = request.get_json()

    # Extract request data
    student_name = data.get("student_name")
    student_id = data.get("student_id")
    course = data.get("course")
    section = data.get("section")
    prof_name = data.get("prof_name")
    program = data.get("program")
    date_filed = data.get("date_filed")
    date_needed = data.get("date_needed")
    time_needed_from = data.get("time_needed_from")
    time_needed_to = data.get("time_needed_to")
    items = data.get("items")  # [{ "item_id": 1, "quantity": 2 }, ...]

    # Validate
    if not all([
        student_name, student_id, course, section, prof_name,
        program, date_filed, date_needed, time_needed_from,
        time_needed_to, items
    ]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Insert into pending_requests
    request_entry = PendingRequest(
        student_name=student_name,
        student_id=student_id,
        course=course,
        section=section,
        prof_name=prof_name,
        program=program,
        date_filed=date_filed,
        date_needed=date_needed,
        time_from=time_needed_from,
        time_to=time_needed_to,
        items=items  # Save as a JSON list directly
    )
    db.session.add(request_entry)
    db.session.commit()

    return jsonify({"success": True, "message": "Request submitted successfully"})



# Add this part to run the server
if __name__ == "__main__":
    with app.app_context():  # NEW: make sure tables are created
        db.create_all()

    app.run(host="0.0.0.0", port=8000)
