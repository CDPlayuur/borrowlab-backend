from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from sqlalchemy.dialects.postgresql import JSONB

app = Flask(__name__)
CORS(app)  # Allow all domains (for testing)

# Configure the PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kdbiPtzehPaslyshovEgqYgfPrMABLfy@postgres.railway.internal:5432/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# CORS(app, origins=["http://borrowlabmaterials.ct.ws"], methods=['GET', 'POST', 'OPTIONS'])

class InventoryItem(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    item_img = db.Column(db.String(255), nullable=True)
    item_stock = db.Column(db.Integer, nullable=False, default=0)
    item_is_consumable = db.Column(db.Boolean, nullable=False, default=False)
    item_desc = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<InventoryItem {self.name}>'

class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'

    pending_request_id = db.Column(db.Integer, primary_key=True)
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
    items = db.Column(JSONB)


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

    print("Received data:", data)

    # Extract request data
    student_name = data.get("student_name")
    student_id = data.get("student_id")
    course = data.get("course")
    section = data.get("section")
    prof_name = data.get("prof_name")
    program = data.get("program")
    date_filed = data.get("date_filed")
    date_needed = data.get("date_needed")
    time_needed_from = data.get("time_from") or '00:00'
    time_needed_to = data.get("time_to") or '23:59'
    items = data.get("items")

    # Print for debugging
    print("Parsed:")
    print("student_name:", student_name)
    print("student_id:", student_id)
    print("course:", course)
    print("section:", section)
    print("prof_name:", prof_name)
    print("program:", program)
    print("date_filed:", date_filed)
    print("date_needed:", date_needed)
    print("time_needed_from:", time_needed_from)
    print("time_needed_to:", time_needed_to)
    print("items:", items)

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
        items=items
    )
    db.session.add(request_entry)
    db.session.commit()

    return jsonify({"success": True, "message": "Request submitted successfully"})

@app.route('/api/sections', methods=['GET'])
def get_sections():
    # Only get requests where status is pending
    sections = db.session.query(PendingRequest.section).filter_by(status='pending').distinct().all()
    result = []
    
    for section in sections:
        # Filter only pending requests in that section
        requests = db.session.query(PendingRequest).filter_by(section=section[0], status='pending').all()
        requests_data = [{
            'student_name': req.student_name,
            'student_id': req.student_id,
            'prof_name': req.prof_name,
            'course': req.course,
            'section': req.section,
            'time_requested': req.time_from.strftime('%H:%M'),  # make it JSON friendly
            'items': req.items,
            'request_id': req.pending_request_id  # pass ID for later approve/deny
        } for req in requests]
        result.append({'section': section[0], 'requests': requests_data})
    
    return jsonify(result)

@app.route('/api/section-names', methods=['GET'])
def get_section_names():
    sections = db.session.query(PendingRequest.section).distinct().all()
    return jsonify([section[0] for section in sections])


# Only change status instead of moving to a new table
@app.route('/api/approve-request', methods=['POST'])
def approve_request():
    data = request.json
    request_id = data['request_id']
    approved_items = data['approved_items']

    request_data = db.session.query(PendingRequest).filter_by(pending_request_id=request_id).first()
    if not request_data:
        return jsonify({'error': 'Request not found'}), 404

    # Deduct stock for each approved item
    for item in approved_items:
        inventory_item = db.session.query(InventoryItem).filter_by(item_id=item['item_id']).first()
        if inventory_item:
            inventory_item.item_stock = max(0, inventory_item.item_stock - item['quantity'])  # avoid negative
    request_data.status = 'approved'
    db.session.commit()

    return jsonify({'status': 'approved'})

# Only change status instead of moving to a new table
@app.route('/api/deny-request', methods=['POST'])
def deny_request():
    data = request.json
    request_id = data['request_id']

    request_data = db.session.query(PendingRequest).filter_by(pending_request_id=request_id).first()
    if not request_data:
        return jsonify({'error': 'Request not found'}), 404

    request_data.status = 'denied'
    db.session.commit()

    return jsonify({'status': 'denied'})

@app.route('/get-requests', methods=['GET'])
def get_all_requests():
    section_filter = request.args.get('section')
    status_filter = request.args.get('status')

    try:
        query = PendingRequest.query

        if section_filter:
            query = query.filter_by(section=section_filter)

        if status_filter:
            query = query.filter_by(status=status_filter)

        requests = query.order_by(PendingRequest.time_created.desc()).all()

        result = [{
            "request_id": r.pending_request_id,
            "student_name": r.student_name,
            "student_id": r.student_id,
            "prof_name": r.prof_name,
            "program": r.program,
            "course": r.course,
            "section": r.section,
            "date_filed": r.date_filed.strftime("%Y-%m-%d"),
            "date_needed": r.date_needed.strftime("%Y-%m-%d"),
            "time_from": r.time_from.strftime("%H:%M"),
            "time_to": r.time_to.strftime("%H:%M"),
            "status": r.status,
            "items": r.items
        } for r in requests]

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-stock', methods=['POST', 'OPTIONS'])
def update_stock():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    updates = data.get('updates', [])

    if not isinstance(updates, list):
        return jsonify({"status": "error", "message": "Invalid updates format"}), 400

    updated_count = 0

    try:
        for update in updates:
            item_id = update.get('item_id')
            new_stock = update.get('new_stock')

            if item_id is None or new_stock is None:
                continue  # skip incomplete data

            item = InventoryItem.query.get(item_id)
            if item:
                print(f"Found item {item.item_name} with stock {item.item_stock}, updating to {new_stock}")
                item.item_stock = new_stock
                updated_count += 1

        db.session.commit()
        print(f"{updated_count} items updated")
        return jsonify({"status": "success", "updated": updated_count}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/finish-request', methods=['POST', 'OPTIONS'])
def finish_request():
    data = request.json
    request_id = data.get('request_id')

    if not request_id:
        return jsonify({'error': 'Request ID is required'}), 400

    request_data = PendingRequest.query.filter_by(pending_request_id=request_id, status='approved').first()
    if not request_data:
        return jsonify({'error': 'Approved request not found'}), 404

    try:
        for item in request_data.items:
            item_id = item.get('item_id')
            quantity = item.get('quantity')

            if item_id and quantity is not None:
                inventory_item = InventoryItem.query.get(item_id)
                if inventory_item:
                    inventory_item.item_stock += quantity  # Add the returned items back to stock

        request_data.status = 'finished'
        db.session.commit()
        return jsonify({'status': 'finished', 'message': f'Request {request_id} marked as finished and stock updated.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=8000)
