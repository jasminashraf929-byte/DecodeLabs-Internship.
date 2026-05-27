# Project 3 — Database Integration
**DecodeLabs Full Stack Internship | Batch 2026**

---

## Overview

Project 3 upgrades the DigitalCraft backend from in-memory storage (Project 2) to a **real SQLite database**. Every contact form submission is now permanently persisted, queryable, and survives server restarts. The frontend gains a **live database dashboard** with real-time CRUD operations.

---

## What Changed From Project 2

| Feature | Project 2 | Project 3 |
|---------|-----------|-----------|
| Storage | In-memory list (lost on restart) | SQLite database (permanent) |
| Schema | None | Typed columns + constraints |
| CRUD | Create, Read, Delete | **Full CRUD** (+ Update/PUT) |
| Endpoints | 5 | **7** (+ PUT, subscribe, stats) |
| Frontend | Contact form only | + Live dashboard, DB stats |

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Backend runtime |
| Flask | Web framework |
| Flask-CORS | Cross-origin request handling |
| **SQLite** | Persistent relational database |
| **sqlite3** | Python's built-in DB driver |
| UUID | Unique message IDs |

---

## Database Schema

### `messages` table
| Column | Type | Constraint |
|--------|------|------------|
| id | TEXT | PRIMARY KEY |
| first_name | TEXT | NOT NULL, CHECK(len ≥ 2) |
| last_name | TEXT | NOT NULL, CHECK(len ≥ 2) |
| email | TEXT | NOT NULL |
| subject | TEXT | DEFAULT 'General' |
| message | TEXT | NOT NULL, CHECK(len ≥ 10) |
| submitted_at | TEXT | NOT NULL |

### `subscribers` table
| Column | Type | Constraint |
|--------|------|------------|
| id | TEXT | PRIMARY KEY |
| email | TEXT | NOT NULL, **UNIQUE** |
| subscribed_at | TEXT | NOT NULL |

---

## API Endpoints

| Method | Endpoint | Description | Code |
|--------|----------|-------------|------|
| GET | `/api/health` | Health check (includes DB status) | 200 |
| GET | `/api/messages` | Retrieve all messages from DB | 200 |
| GET | `/api/messages/<id>` | Retrieve one message | 200/404 |
| POST | `/api/contact` | Submit + INSERT into DB | 201/400 |
| **PUT** | `/api/messages/<id>` | **Update subject/message** | 200/404 |
| DELETE | `/api/messages/<id>` | DELETE from DB | 204/404 |
| GET | `/api/stats` | DB row counts + metadata | 200 |
| POST | `/api/subscribe` | Add email (UNIQUE enforced) | 201/409 |

---

## File Structure

```
project3/
├── app.py            ← Flask backend with SQLite integration
├── index.html        ← Upgraded frontend with live DB dashboard
├── requirements.txt  ← Python dependencies
├── README.md         ← This file
└── digitalcraft.db   ← SQLite database (auto-created on first run)
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
The database file `digitalcraft.db` is created automatically on first run.

### Step 3 — Open the frontend
Open `index.html` in your browser. The green dot confirms the API + DB are connected.

---

## Key Requirements Met

- [x] Database schema designed (2 tables with proper constraints)
- [x] Full CRUD operations implemented (Create, Read, Update, Delete)
- [x] SQLite used via Python's built-in `sqlite3` driver (no ORM)
- [x] Parameterized queries (SQL injection protected)
- [x] Schema-level integrity: NOT NULL, CHECK, UNIQUE, PRIMARY KEY
- [x] FOREIGN_KEYS pragma enabled
- [x] Data persists across server restarts
- [x] Live frontend dashboard reads from database in real time
- [x] DB health status shown in `/api/health` response

---

## Security: Parameterized Queries

All SQL uses `?` placeholders — user input is **never** concatenated:

```python
# ✅ Safe — parameterized
conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,))

# ❌ Vulnerable — never do this
conn.execute(f"SELECT * FROM messages WHERE id = '{message_id}'")
```

---

*Prepared by: [jasmin ashraf] | DecodeLabs Intern | Batch 2026*
