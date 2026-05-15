import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "splitwise.db"


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL DEFAULT 'local_user@example.com',
            filename TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            restaurant_name TEXT DEFAULT '',
            total_food REAL NOT NULL DEFAULT 0,
            gst REAL NOT NULL DEFAULT 0,
            grand_total REAL NOT NULL DEFAULT 0,
            num_items INTEGER NOT NULL DEFAULT 0,
            num_people INTEGER NOT NULL DEFAULT 0,
            raw_ocr_text TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS receipt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL DEFAULT 0,
            total_price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS splits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER NOT NULL,
            person_name TEXT NOT NULL,
            food_amount REAL NOT NULL DEFAULT 0,
            gst_amount REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS split_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            split_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (split_id) REFERENCES splits(id) ON DELETE CASCADE
        );
    """)

    # Try to add user_email column for existing databases
    try:
        cursor.execute("ALTER TABLE receipts ADD COLUMN user_email TEXT NOT NULL DEFAULT 'local_user@example.com'")
    except sqlite3.OperationalError:
        pass # Column already exists

    conn.commit()
    conn.close()


def save_receipt(user_email, filename, upload_date, total_food, gst, grand_total,
                 num_items, num_people, raw_ocr_text, items, splits_data, assignments):
    """
    Save a complete receipt with items and splits to the database.
    Returns the receipt_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert receipt
        cursor.execute("""
            INSERT INTO receipts (user_email, filename, upload_date, total_food, gst, grand_total,
                                  num_items, num_people, raw_ocr_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_email, filename, upload_date, total_food, gst, grand_total,
              num_items, num_people, raw_ocr_text))
        receipt_id = cursor.lastrowid

        # Insert items
        for item in items:
            cursor.execute("""
                INSERT INTO receipt_items (receipt_id, item_name, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (receipt_id, item["item"], item["quantity"],
                  item["unit_price"], item["price"]))

        # Insert splits
        for person, breakdown in splits_data.items():
            cursor.execute("""
                INSERT INTO splits (receipt_id, person_name, food_amount, gst_amount, total_amount)
                VALUES (?, ?, ?, ?, ?)
            """, (receipt_id, person, breakdown["food"],
                  breakdown["gst"], breakdown["total"]))
            split_id = cursor.lastrowid

            # Insert split items
            person_items = assignments.get(person, [])
            for si in person_items:
                cursor.execute("""
                    INSERT INTO split_items (split_id, item_name, price)
                    VALUES (?, ?, ?)
                """, (split_id, si["item"], si["price"]))

        conn.commit()
        return receipt_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_receipts(user_email):
    """Get all receipts for the user ordered by date."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM receipts 
        WHERE user_email = ? 
        ORDER BY upload_date DESC, id DESC
    """, (user_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_receipt_details(receipt_id, user_email):
    """Get a single receipt with its items and splits (verifying ownership)."""
    conn = get_connection()

    receipt_row = conn.execute(
        "SELECT * FROM receipts WHERE id = ? AND user_email = ?", (receipt_id, user_email)
    ).fetchone()
    
    if not receipt_row:
        conn.close()
        return None

    receipt = dict(receipt_row)

    items = [dict(r) for r in conn.execute(
        "SELECT * FROM receipt_items WHERE receipt_id = ?", (receipt_id,)
    ).fetchall()]

    splits = [dict(r) for r in conn.execute(
        "SELECT * FROM splits WHERE receipt_id = ?", (receipt_id,)
    ).fetchall()]

    for split in splits:
        split["items"] = [dict(r) for r in conn.execute(
            "SELECT * FROM split_items WHERE split_id = ?", (split["id"],)
        ).fetchall()]

    conn.close()
    return {"receipt": receipt, "items": items, "splits": splits}


def get_spending_over_time(user_email):
    """Get daily spending totals for the user."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT upload_date, SUM(grand_total) as total, COUNT(*) as num_receipts
        FROM receipts
        WHERE user_email = ?
        GROUP BY upload_date
        ORDER BY upload_date
    """, (user_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_per_person_spending(user_email):
    """Get total spending per person across all user's receipts."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.person_name, 
               SUM(s.food_amount) as total_food,
               SUM(s.gst_amount) as total_gst,
               SUM(s.total_amount) as total_spent,
               COUNT(*) as num_splits
        FROM splits s
        JOIN receipts r ON s.receipt_id = r.id
        WHERE r.user_email = ?
        GROUP BY s.person_name
        ORDER BY total_spent DESC
    """, (user_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_items(user_email, limit=15):
    """Get most frequently ordered items for the user."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT ri.item_name, 
               SUM(ri.quantity) as total_qty,
               ROUND(AVG(ri.unit_price), 2) as avg_price,
               SUM(ri.total_price) as total_spent
        FROM receipt_items ri
        JOIN receipts r ON ri.receipt_id = r.id
        WHERE r.user_email = ?
        GROUP BY ri.item_name
        ORDER BY total_qty DESC
        LIMIT ?
    """, (user_email, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_summary_stats(user_email):
    """Get overall summary statistics for the user."""
    conn = get_connection()
    stats = dict(conn.execute("""
        SELECT 
            COUNT(*) as total_receipts,
            COALESCE(SUM(grand_total), 0) as total_spent,
            COALESCE(AVG(grand_total), 0) as avg_bill,
            COALESCE(MAX(grand_total), 0) as max_bill,
            COALESCE(MIN(grand_total), 0) as min_bill,
            COALESCE(SUM(gst), 0) as total_gst,
            COALESCE(SUM(num_items), 0) as total_items
        FROM receipts
        WHERE user_email = ?
    """, (user_email,)).fetchone())

    people_count = conn.execute("""
        SELECT COUNT(DISTINCT s.person_name) as count 
        FROM splits s
        JOIN receipts r ON s.receipt_id = r.id
        WHERE r.user_email = ?
    """, (user_email,)).fetchone()
    stats["unique_people"] = people_count["count"] if people_count else 0

    conn.close()
    return stats


def delete_receipt(receipt_id, user_email):
    """Delete a receipt and all related data (cascades), verifying ownership."""
    conn = get_connection()
    conn.execute("DELETE FROM receipts WHERE id = ? AND user_email = ?", (receipt_id, user_email))
    conn.commit()
    conn.close()


# Initialize database on import
init_db()
