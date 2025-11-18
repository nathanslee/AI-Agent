import sqlite3
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class DatabaseManager:
    """Manages SQLite database operations for the AI Database Assistant"""

    def __init__(self, database_dir: str = "./databases"):
        self.database_dir = Path(database_dir)
        self.database_dir.mkdir(exist_ok=True)
        self.global_db_path = self.database_dir / "global.db"
        self._init_global_database()

    def _init_global_database(self):
        """Initialize the global master database"""
        conn = sqlite3.connect(str(self.global_db_path))
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # User databases metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_databases (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                db_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                schema_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Plaid tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plaid_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                access_token TEXT NOT NULL,
                item_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        conn.commit()
        conn.close()

    def get_global_connection(self):
        """Get connection to global database"""
        return sqlite3.connect(str(self.global_db_path))

    def create_user(self, email: str, hashed_password: str) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        conn = self.get_global_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (id, email, hashed_password, created_at) VALUES (?, ?, ?, ?)",
                (user_id, email, hashed_password, datetime.utcnow().isoformat())
            )
            conn.commit()

            # Create user's database directory
            user_dir = self.database_dir / f"user_{user_id}"
            user_dir.mkdir(exist_ok=True)

            return user_id
        except sqlite3.IntegrityError:
            raise ValueError("Email already exists")
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self.get_global_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, hashed_password, created_at FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "email": row[1],
                "hashed_password": row[2],
                "created_at": row[3]
            }
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_global_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "email": row[1],
                "created_at": row[2]
            }
        return None

    def create_user_database(self, user_id: str, db_name: str, display_name: str, schema: Dict[str, Any]) -> str:
        """Create a new database for a user"""
        db_id = str(uuid.uuid4())
        user_dir = self.database_dir / f"user_{user_id}"
        user_dir.mkdir(exist_ok=True)

        # Sanitize database name for filename
        safe_db_name = "".join(c for c in db_name if c.isalnum() or c in "._- ").strip()
        db_file_path = user_dir / f"{safe_db_name}.db"

        # Create the user's database with schema
        conn = sqlite3.connect(str(db_file_path))
        cursor = conn.cursor()

        # Build CREATE TABLE statement from schema
        columns = []
        for field in schema.get("fields", []):
            field_name = field["name"]
            field_type = field.get("type", "TEXT")
            optional = field.get("optional", False)

            col_def = f"{field_name} {field_type}"
            if not optional:
                col_def += " NOT NULL"
            columns.append(col_def)

        # Add ID and created_at
        columns.insert(0, "id TEXT PRIMARY KEY")
        columns.append("created_at TEXT NOT NULL")

        create_table_sql = f"CREATE TABLE {db_name} ({', '.join(columns)})"
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()

        # Store metadata in global database
        global_conn = self.get_global_connection()
        global_cursor = global_conn.cursor()
        global_cursor.execute(
            """INSERT INTO user_databases
               (id, user_id, db_name, display_name, file_path, schema_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (db_id, user_id, db_name, display_name, str(db_file_path), json.dumps(schema), datetime.utcnow().isoformat())
        )
        global_conn.commit()
        global_conn.close()

        return db_id

    def get_user_databases(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all databases for a user"""
        conn = self.get_global_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, db_name, display_name, schema_json, created_at FROM user_databases WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        databases = []
        for row in rows:
            databases.append({
                "id": row[0],
                "db_name": row[1],
                "display_name": row[2],
                "schema": json.loads(row[3]),
                "created_at": row[4]
            })
        return databases

    def get_database_by_id(self, db_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get database metadata by ID (with user authorization)"""
        conn = self.get_global_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_id, db_name, display_name, file_path, schema_json, created_at
               FROM user_databases WHERE id = ? AND user_id = ?""",
            (db_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "db_name": row[2],
                "display_name": row[3],
                "file_path": row[4],
                "schema": json.loads(row[5]),
                "created_at": row[6]
            }
        return None

    def delete_database(self, db_id: str, user_id: str) -> bool:
        """Delete a user's database"""
        db_info = self.get_database_by_id(db_id, user_id)
        if not db_info:
            return False

        # Delete the database file
        db_path = Path(db_info["file_path"])
        if db_path.exists():
            db_path.unlink()

        # Remove from metadata
        conn = self.get_global_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_databases WHERE id = ? AND user_id = ?", (db_id, user_id))
        conn.commit()
        conn.close()

        return True

    def execute_query(self, db_id: str, user_id: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query on a user's database"""
        db_info = self.get_database_by_id(db_id, user_id)
        if not db_info:
            raise ValueError("Database not found or access denied")

        conn = sqlite3.connect(db_info["file_path"])
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
            else:
                conn.commit()
                result = [{"affected_rows": cursor.rowcount}]

            return result
        finally:
            conn.close()

    def insert_data(self, db_id: str, user_id: str, data: Dict[str, Any]) -> str:
        """Insert data into a user's database"""
        db_info = self.get_database_by_id(db_id, user_id)
        if not db_info:
            raise ValueError("Database not found or access denied")

        # Add ID and timestamp
        record_id = str(uuid.uuid4())
        data_with_meta = {
            "id": record_id,
            **data,
            "created_at": datetime.utcnow().isoformat()
        }

        # Build INSERT statement
        table_name = db_info["db_name"]
        columns = ", ".join(data_with_meta.keys())
        placeholders = ", ".join(["?" for _ in data_with_meta])
        values = tuple(data_with_meta.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        conn = sqlite3.connect(db_info["file_path"])
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return record_id

    def get_all_data(self, db_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all data from a user's database"""
        db_info = self.get_database_by_id(db_id, user_id)
        if not db_info:
            raise ValueError("Database not found or access denied")

        table_name = db_info["db_name"]
        query = f"SELECT * FROM {table_name} ORDER BY created_at DESC"

        return self.execute_query(db_id, user_id, query)

    def save_plaid_token(self, user_id: str, access_token: str, item_id: str) -> str:
        """Save Plaid access token for user"""
        token_id = str(uuid.uuid4())
        conn = self.get_global_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO plaid_tokens (id, user_id, access_token, item_id, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (token_id, user_id, access_token, item_id, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

        return token_id

    def get_plaid_token(self, user_id: str) -> Optional[str]:
        """Get Plaid access token for user"""
        conn = self.get_global_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT access_token FROM plaid_tokens WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None


# Global instance
db_manager = DatabaseManager()
