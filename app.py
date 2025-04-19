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
    __tablename__ = "pending_requests"  # Specify the table name to match the new table

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    professor_name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(50), nullable=False)
    date_filed = db.Column(db.Date, nullable=False)
    date_needed = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    items = db.Column(db.JSON, nullable=False)  # Store as JSONB in PostgreSQL
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())


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
    professor_name = data.get("professor_name")
    program = data.get("program")
    date_filed = data.get("date_filed")
    date_needed = data.get("date_needed")
    time_needed_from = data.get("time_needed_from")
    time_needed_to = data.get("time_needed_to")
    items = data.get("items")  # [{ "item_id": 1, "quantity": 2 }, ...]

    # Validate
    if not all([
        student_name, student_id, course, section, professor_name,
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
        professor_name=professor_name,
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
