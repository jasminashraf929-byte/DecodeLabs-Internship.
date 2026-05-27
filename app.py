"""
DecodeLabs Project 2 — Backend API Development
Flask REST API for DigitalCraft Portfolio Contact System
Author: DecodeLabs Intern | Batch 2026
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re
import uuid

# ─────────────────────────────────────────────
#  App Initialisation
# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow requests from the frontend HTML file

# In-memory data store (acts like a simple database)
messages_db = []


# ─────────────────────────────────────────────
#  Helper: Validation
# ─────────────────────────────────────────────
def is_valid_email(email):
    """Syntactic validation — checks email format."""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))


def validate_contact_payload(data):
    """
    Gatekeeper Rule: Never Trust the Client.
    Returns (is_valid: bool, errors: list)
    """
    errors = []

    # Required fields check
    required = ['first_name', 'last_name', 'email', 'message']
    for field in required:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"'{field}' is required and cannot be empty.")

    # Email format check
    if data.get('email') and not is_valid_email(data['email']):
        errors.append("'email' must be a valid email address.")

    # Length constraints
    if data.get('first_name') and len(data['first_name'].strip()) < 2:
        errors.append("'first_name' must be at least 2 characters.")

    if data.get('last_name') and len(data['last_name'].strip()) < 2:
        errors.append("'last_name' must be at least 2 characters.")

    if data.get('message') and len(data['message'].strip()) < 10:
        errors.append("'message' must be at least 10 characters.")

    return len(errors) == 0, errors


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

# GET /api/health
# Purpose  : Server health check — confirm the API is alive
# Response : 200 OK
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "DigitalCraft API is running.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }), 200


# GET /api/messages
# Purpose  : Retrieve all stored contact messages
# Response : 200 OK — list of messages
@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify({
        "status": "success",
        "count": len(messages_db),
        "messages": messages_db
    }), 200


# GET /api/messages/<id>
# Purpose  : Retrieve a single message by its ID
# Response : 200 OK | 404 Not Found
@app.route('/api/messages/<string:message_id>', methods=['GET'])
def get_message(message_id):
    message = next((m for m in messages_db if m['id'] == message_id), None)

    if not message:
        return jsonify({
            "status": "error",
            "message": f"Message with id '{message_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "message": message
    }), 200


# POST /api/contact
# Purpose  : Accept a new contact form submission
# Body     : JSON { first_name, last_name, email, subject, message }
# Response : 201 Created | 400 Bad Request
@app.route('/api/contact', methods=['POST'])
def submit_contact():

    # Step 1 — Ensure Content-Type is JSON
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Content-Type must be 'application/json'."
        }), 400

    data = request.get_json()

    # Step 2 — Validate the payload (Gatekeeper Rule)
    is_valid, errors = validate_contact_payload(data)

    if not is_valid:
        return jsonify({
            "status": "error",
            "message": "Validation failed. Please fix the errors below.",
            "errors": errors
        }), 400

    # Step 3 — Build the message record
    new_message = {
        "id":         str(uuid.uuid4()),
        "first_name": data['first_name'].strip(),
        "last_name":  data['last_name'].strip(),
        "email":      data['email'].strip().lower(),
        "subject":    data.get('subject', 'General').strip() or 'General',
        "message":    data['message'].strip(),
        "submitted_at": datetime.utcnow().isoformat() + "Z"
    }

    # Step 4 — Store it
    messages_db.append(new_message)

    # Step 5 — Respond with 201 Created
    return jsonify({
        "status": "success",
        "message": "Your message has been received. We will get back to you soon!",
        "data": new_message
    }), 201


# DELETE /api/messages/<id>
# Purpose  : Delete a message by ID
# Response : 204 No Content | 404 Not Found
@app.route('/api/messages/<string:message_id>', methods=['DELETE'])
def delete_message(message_id):
    global messages_db
    original_count = len(messages_db)
    messages_db = [m for m in messages_db if m['id'] != message_id]

    if len(messages_db) == original_count:
        return jsonify({
            "status": "error",
            "message": f"Message with id '{message_id}' not found."
        }), 404

    return '', 204  # 204 No Content — deletion successful, no body needed


# ─────────────────────────────────────────────
#  Global Error Handlers
# ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "The requested endpoint does not exist.",
        "code": 404
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "status": "error",
        "message": "HTTP method not allowed on this endpoint.",
        "code": 405
    }), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "status": "error",
        "message": "An internal server error occurred.",
        "code": 500
    }), 500


# ─────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("  DigitalCraft API — DecodeLabs Project 2")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
