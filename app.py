"""
DecodeLabs Project 3 — Database Integration
Flask REST API with SQLite persistence for DigitalCraft Portfolio
Author: DecodeLabs Intern | Batch 2026
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import re
import uuid
import sqlite3
import os

# ─────────────────────────────────────────────
#  App Initialisation
# ─────────────────────────────────────────────
app = Flask(__name__, static_folder='.')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'digitalcraft.db')


# ─────────────────────────────────────────────
#  Database Setup
# ─────────────────────────────────────────────
def get_db():
    """Return a database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Create all tables if they don't exist.
    Schema design: messages table for contact form submissions.
    """
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id           TEXT PRIMARY KEY,
                first_name   TEXT NOT NULL CHECK(length(trim(first_name)) >= 2),
                last_name    TEXT NOT NULL CHECK(length(trim(last_name))  >= 2),
                email        TEXT NOT NULL,
                subject      TEXT NOT NULL DEFAULT 'General',
                message      TEXT NOT NULL CHECK(length(trim(message))    >= 10),
                submitted_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subscribers (
                id           TEXT PRIMARY KEY,
                email        TEXT NOT NULL UNIQUE,
                subscribed_at TEXT NOT NULL
            );
        """)
    print("  ✓ Database initialised:", DB_PATH)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def is_valid_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))


def validate_contact_payload(data):
    errors = []
    for field in ['first_name', 'last_name', 'email', 'message']:
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"'{field}' is required and cannot be empty.")
    if data.get('email') and not is_valid_email(data['email']):
        errors.append("'email' must be a valid email address.")
    if data.get('first_name') and len(data['first_name'].strip()) < 2:
        errors.append("'first_name' must be at least 2 characters.")
    if data.get('last_name') and len(data['last_name'].strip()) < 2:
        errors.append("'last_name' must be at least 2 characters.")
    if data.get('message') and len(data['message'].strip()) < 10:
        errors.append("'message' must be at least 10 characters.")
    return len(errors) == 0, errors


def row_to_dict(row):
    return dict(row) if row else None


# ─────────────────────────────────────────────
#  Serve Frontend
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

# GET /api/health
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "error"

    return jsonify({
        "status": "ok",
        "message": "DigitalCraft API is running.",
        "database": db_status,
        "db_path": DB_PATH,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0"
    }), 200


# GET /api/messages
@app.route('/api/messages', methods=['GET'])
def get_messages():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM messages ORDER BY submitted_at DESC"
        ).fetchall()
    messages = [row_to_dict(r) for r in rows]
    return jsonify({
        "status": "success",
        "count": len(messages),
        "messages": messages
    }), 200


# GET /api/messages/<id>
@app.route('/api/messages/<string:message_id>', methods=['GET'])
def get_message(message_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM messages WHERE id = ?", (message_id,)
        ).fetchone()
    if not row:
        return jsonify({
            "status": "error",
            "message": f"Message with id '{message_id}' not found."
        }), 404
    return jsonify({"status": "success", "message": row_to_dict(row)}), 200


# POST /api/contact
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Content-Type must be 'application/json'."
        }), 400

    data = request.get_json()
    is_valid, errors = validate_contact_payload(data)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": "Validation failed. Please fix the errors below.",
            "errors": errors
        }), 400

    new_message = {
        "id":           str(uuid.uuid4()),
        "first_name":   data['first_name'].strip(),
        "last_name":    data['last_name'].strip(),
        "email":        data['email'].strip().lower(),
        "subject":      data.get('subject', 'General').strip() or 'General',
        "message":      data['message'].strip(),
        "submitted_at": datetime.utcnow().isoformat() + "Z"
    }

    try:
        with get_db() as conn:
            conn.execute(
                """INSERT INTO messages
                   (id, first_name, last_name, email, subject, message, submitted_at)
                   VALUES (:id, :first_name, :last_name, :email, :subject, :message, :submitted_at)""",
                new_message
            )
    except sqlite3.IntegrityError as e:
        return jsonify({
            "status": "error",
            "message": "Database constraint violation.",
            "detail": str(e)
        }), 400

    return jsonify({
        "status": "success",
        "message": "Your message has been received and saved to the database!",
        "data": new_message
    }), 201


# PUT /api/messages/<id>  — NEW in Project 3 (full CRUD)
@app.route('/api/messages/<string:message_id>', methods=['PUT'])
def update_message(message_id):
    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type must be 'application/json'."}), 400

    data = request.get_json()

    with get_db() as conn:
        row = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
        if not row:
            return jsonify({"status": "error", "message": f"Message with id '{message_id}' not found."}), 404

        # Only allow updating subject and message body
        subject = data.get('subject', row['subject']).strip() or 'General'
        message = data.get('message', row['message']).strip()

        if len(message) < 10:
            return jsonify({"status": "error", "message": "'message' must be at least 10 characters."}), 400

        conn.execute(
            "UPDATE messages SET subject = ?, message = ? WHERE id = ?",
            (subject, message, message_id)
        )
        updated = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()

    return jsonify({"status": "success", "message": row_to_dict(updated)}), 200


# DELETE /api/messages/<id>
@app.route('/api/messages/<string:message_id>', methods=['DELETE'])
def delete_message(message_id):
    with get_db() as conn:
        result = conn.execute(
            "DELETE FROM messages WHERE id = ?", (message_id,)
        )
        if result.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": f"Message with id '{message_id}' not found."
            }), 404
    return '', 204


# POST /api/subscribe  — bonus endpoint
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type must be 'application/json'."}), 400

    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email or not is_valid_email(email):
        return jsonify({"status": "error", "message": "'email' must be a valid email address."}), 400

    record = {
        "id": str(uuid.uuid4()),
        "email": email,
        "subscribed_at": datetime.utcnow().isoformat() + "Z"
    }

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO subscribers (id, email, subscribed_at) VALUES (:id, :email, :subscribed_at)",
                record
            )
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "This email is already subscribed."}), 409

    return jsonify({"status": "success", "message": "Subscribed successfully!", "data": record}), 201


# GET /api/stats  — database stats endpoint
@app.route('/api/stats', methods=['GET'])
def get_stats():
    with get_db() as conn:
        msg_count    = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        sub_count    = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
        latest       = conn.execute("SELECT submitted_at FROM messages ORDER BY submitted_at DESC LIMIT 1").fetchone()
        latest_at    = latest[0] if latest else None

    return jsonify({
        "status": "success",
        "stats": {
            "total_messages":    msg_count,
            "total_subscribers": sub_count,
            "latest_message_at": latest_at
        }
    }), 200


# ─────────────────────────────────────────────
#  Global Error Handlers
# ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "The requested endpoint does not exist.", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "message": "HTTP method not allowed on this endpoint.", "code": 405}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "error", "message": "An internal server error occurred.", "code": 500}), 500


# ─────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("=" * 55)
    print("  DigitalCraft API v2 — DecodeLabs Project 3")
    print("  Database: SQLite →", DB_PATH)
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)
