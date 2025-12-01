"""
Database handling for NexSupply app.
Manages SQLite database operations for storing requests and leads.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

DB_PATH = "nexsupply.db"


def init_db() -> None:
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            input_text TEXT,
            input_type TEXT,
            ai_response TEXT,
            detected_language TEXT
        )
    """)
    
    # Create leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            email TEXT NOT NULL,
            request_id INTEGER,
            FOREIGN KEY (request_id) REFERENCES requests(id)
        )
    """)
    
    conn.commit()
    conn.close()


def insert_request(
    input_text: Optional[str] = None,
    input_type: str = "text",
    ai_response: Optional[str] = None,
    detected_language: Optional[str] = None
) -> int:
    """Insert a new request into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO requests (timestamp, input_text, input_type, ai_response, detected_language)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, input_text, input_type, json.dumps(ai_response) if ai_response else None, detected_language))
    
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return request_id


def insert_lead(email: str, request_id: Optional[int] = None) -> int:
    """Insert a new lead into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO leads (timestamp, email, request_id)
        VALUES (?, ?, ?)
    """, (timestamp, email, request_id))
    
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return lead_id


def get_all_requests(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve all requests from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM requests
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_leads(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve all leads from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM leads
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_request_by_id(request_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a specific request by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM requests
        WHERE id = ?
    """, (request_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        # Parse JSON response
        if result.get('ai_response'):
            try:
                result['ai_response'] = json.loads(result['ai_response'])
            except (json.JSONDecodeError, TypeError):
                result['ai_response'] = {}
        return result
    return None


def get_recent_requests_for_comparison(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent requests for comparison, excluding the current one."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, timestamp, input_text, input_type, detected_language
        FROM requests
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

