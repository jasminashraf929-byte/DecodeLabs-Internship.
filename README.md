# Project 2 — Backend API Development
**DecodeLabs Full Stack Internship | Batch 2026**

---

## Overview

A RESTful backend API built with Python Flask that powers the contact form from Project 1. The frontend (`index.html`) is fully integrated — form submissions hit the real Flask server, which validates input, stores messages in memory, and returns proper JSON responses with correct HTTP status codes.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Backend runtime |
| Flask | Web framework |
| Flask-CORS | Cross-origin request handling |
| JSON | Data exchange format |
| UUID | Unique message IDs |

---

## API Endpoints

| Method | Endpoint | Description | Success Code |
|--------|----------|-------------|--------------|
| GET | `/api/health` | Server health check | 200 |
| GET | `/api/messages` | Retrieve all messages | 200 |
| GET | `/api/messages/<id>` | Retrieve one message by ID | 200 |
| POST | `/api/contact` | Submit a contact message | 201 |
| DELETE | `/api/messages/<id>` | Delete a message by ID | 204 |

---

## HTTP Status Codes Used

| Code | Meaning | When Returned |
|------|---------|---------------|
| 200 | OK | Successful GET request |
| 201 | Created | Message successfully saved |
| 204 | No Content | Message successfully deleted |
| 400 | Bad Request | Validation failed |
| 404 | Not Found | Message ID does not exist |
| 405 | Method Not Allowed | Wrong HTTP method used |
| 500 | Internal Server Error | Unexpected server error |

---

## Validation Rules (The Gatekeeper)

| Field | Rules |
|-------|-------|
| `first_name` | Required, minimum 2 characters |
| `last_name` | Required, minimum 2 characters |
| `email` | Required, valid email format |
| `message` | Required, minimum 10 characters |
| `subject` | Optional |

---

## File Structure

```
project2/
├── app.py            ← Flask backend — all API logic
├── index.html        ← Project 1 frontend integrated with real API
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## How to Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Start the Flask server
```bash
python app.py
```
Server runs at: **http://127.0.0.1:5000**

### Step 3 — Open the frontend
Open `index.html` in your browser. The dot next to the logo turns **green** when the API is connected.

---

## API Request & Response Examples

### POST /api/contact — Success (201)
**Request:**
```json
{
  "first_name": "Merna",
  "last_name": "Ashraf",
  "email": "merna@example.com",
  "subject": "Feedback",
  "message": "Great internship project!"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Your message has been received. We will get back to you soon!",
  "data": {
    "id": "a1b2c3d4-...",
    "first_name": "Merna",
    "last_name": "Ashraf",
    "email": "merna@example.com",
    "subject": "Feedback",
    "message": "Great internship project!",
    "submitted_at": "2026-05-21T12:00:00Z"
  }
}
```

### POST /api/contact — Validation Error (400)
**Response:**
```json
{
  "status": "error",
  "message": "Validation failed. Please fix the errors below.",
  "errors": [
    "'email' must be a valid email address.",
    "'message' must be at least 10 characters."
  ]
}
```

### GET /api/health — Response (200)
```json
{
  "status": "ok",
  "message": "DigitalCraft API is running.",
  "timestamp": "2026-05-21T12:00:00Z",
  "version": "1.0.0"
}
```

---

## Testing with curl

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Submit a contact message
curl -X POST http://127.0.0.1:5000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Merna","last_name":"Ashraf","email":"merna@example.com","subject":"Feedback","message":"Great internship project!"}'

# Get all messages
curl http://127.0.0.1:5000/api/messages

# Get one message by ID
curl http://127.0.0.1:5000/api/messages/<id>

# Delete a message
curl -X DELETE http://127.0.0.1:5000/api/messages/<id>
```

---

## Key Requirements Met

- [x] GET endpoints implemented (`/health`, `/messages`, `/messages/<id>`)
- [x] POST endpoint implemented (`/contact`)
- [x] User input handled and parsed from JSON body
- [x] Basic data validation with descriptive error messages
- [x] Correct HTTP status codes returned
- [x] JSON responses throughout
- [x] CORS enabled for frontend integration
- [x] Connected to Project 1 frontend via `fetch()`

---



---

*Prepared by: [jasmin ashraf] | DecodeLabs Intern | Batch 2026*
