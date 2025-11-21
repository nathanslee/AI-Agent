import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class DatabaseManager:
    """Manages PostgreSQL database operations for DataBuddy using Supabase"""

    def __init__(self):
        # Get Supabase connection URL from environment
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required for Supabase connection")

        # Create connection pool
        self.pool = SimpleConnectionPool(1, 20, self.database_url)
        self._init_global_database()

    def _get_connection(self):
        """Get a connection from the pool"""
        return self.pool.getconn()

    def _release_connection(self, conn):
        """Release a connection back to the pool"""
        self.pool.putconn(conn)

    def _init_global_database(self):
        """Initialize the global master database tables"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)

            # User databases metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_databases (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    db_name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    schema_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # Plaid tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plaid_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # Google Calendar tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS google_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT UNIQUE NOT NULL,
                    token_data TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # Create index for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_databases_user_id
                ON user_databases(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_plaid_tokens_user_id
                ON plaid_tokens(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_google_tokens_user_id
                ON google_tokens(user_id)
            """)

            conn.commit()
        finally:
            cursor.close()
            self._release_connection(conn)

    def create_user(self, email: str, hashed_password: str) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, email, hashed_password, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, email, hashed_password, datetime.utcnow())
            )
            conn.commit()
            return user_id
        except psycopg2.IntegrityError:
            conn.rollback()
            raise ValueError("Email already exists")
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, email, hashed_password, created_at FROM users WHERE email = %s",
                (email,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    "id": row["id"],
                    "email": row["email"],
                    "hashed_password": row["hashed_password"],
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"])
                }
            return None
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, email, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    "id": row["id"],
                    "email": row["email"],
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"])
                }
            return None
        finally:
            cursor.close()
            self._release_connection(conn)

    def create_user_database(self, user_id: str, db_name: str, display_name: str, schema: Dict[str, Any]) -> str:
        """Create a new database table for a user"""
        db_id = str(uuid.uuid4())
        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            # Sanitize table name (use user_id prefix to ensure uniqueness and isolation)
            safe_table_name = f"user_{user_id.replace('-', '_')}_{db_name.lower().replace(' ', '_').replace('-', '_')}"
            # Limit table name to PostgreSQL's 63 character limit
            if len(safe_table_name) > 63:
                safe_table_name = safe_table_name[:63]

            # Build CREATE TABLE statement from schema
            columns = []
            for field in schema.get("fields", []):
                field_name = field["name"].lower().replace(' ', '_')
                field_type = field.get("type", "TEXT")
                optional = field.get("optional", False)

                # Map SQLite types to PostgreSQL types
                if field_type.upper() == "INTEGER":
                    pg_type = "INTEGER"
                elif field_type.upper() == "REAL":
                    pg_type = "REAL"
                elif field_type.upper() == "DATE":
                    pg_type = "DATE"
                else:
                    pg_type = "TEXT"

                col_def = f"{field_name} {pg_type}"
                if not optional:
                    col_def += " NOT NULL"
                columns.append(col_def)

            # Add ID and created_at
            columns.insert(0, "id TEXT PRIMARY KEY")
            columns.append("created_at TIMESTAMP NOT NULL DEFAULT NOW()")

            create_table_sql = f"CREATE TABLE {safe_table_name} ({', '.join(columns)})"
            cursor.execute(create_table_sql)

            # Update schema with actual table name
            schema["database_name"] = safe_table_name

            # Store metadata in user_databases table
            cursor.execute(
                """INSERT INTO user_databases
                   (id, user_id, db_name, display_name, schema_json, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (db_id, user_id, safe_table_name, display_name, json.dumps(schema), datetime.utcnow())
            )

            conn.commit()
            return db_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_user_databases(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all databases for a user"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT id, db_name, display_name, schema_json, created_at FROM user_databases WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()

            databases = []
            for row in rows:
                databases.append({
                    "id": row["id"],
                    "db_name": row["db_name"],
                    "display_name": row["display_name"],
                    "schema": json.loads(row["schema_json"]),
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"])
                })
            return databases
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_database_by_id(self, db_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get database metadata by ID (with user authorization)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """SELECT id, user_id, db_name, display_name, schema_json, created_at
                   FROM user_databases WHERE id = %s AND user_id = %s""",
                (db_id, user_id)
            )
            row = cursor.fetchone()

            if row:
                return {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "db_name": row["db_name"],
                    "display_name": row["display_name"],
                    "schema": json.loads(row["schema_json"]),
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"])
                }
            return None
        finally:
            cursor.close()
            self._release_connection(conn)

    def delete_database(self, db_id: str, user_id: str) -> bool:
        """Delete a user's database"""
        db_info = self.get_database_by_id(db_id, user_id)
        if not db_info:
            return False

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Drop the user's table
            table_name = db_info["db_name"]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Remove from metadata
            cursor.execute(
                "DELETE FROM user_databases WHERE id = %s AND user_id = %s",
                (db_id, user_id)
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)

    def execute_query(self, db_id: str, user_id: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query on a user's database"""
        db_info = self.get_database_by_id(db_id, user_id)
        if not db_info:
            raise ValueError("Database not found or access denied")

        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Auto-inject id and created_at for INSERT statements
            query_upper = query.strip().upper()
            if query_upper.startswith("INSERT"):
                import re
                # Parse INSERT statement to add id and created_at
                print(f"DEBUG: Original query: {query}")
                match = re.match(r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', query, re.IGNORECASE)
                print(f"DEBUG: Regex match: {match}")
                if match:
                    table_name = match.group(1)
                    columns = match.group(2)
                    values = match.group(3)
                    print(f"DEBUG: Matched - table: {table_name}, columns: {columns}, values: {values}")

                    # Add id and created_at to columns and values
                    new_columns = f"id, {columns}, created_at"
                    # Generate UUID for id
                    record_id = str(uuid.uuid4())
                    new_values = f"'{record_id}', {values}, NOW()"

                    query = f"INSERT INTO {table_name} ({new_columns}) VALUES ({new_values})"
                    print(f"DEBUG: Modified query: {query}")
                else:
                    print(f"DEBUG: Regex did not match!")

            cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    row_dict = dict(row)
                    # Convert datetime objects to ISO strings
                    for key, value in row_dict.items():
                        if hasattr(value, "isoformat"):
                            row_dict[key] = value.isoformat()
                    result.append(row_dict)
            else:
                conn.commit()
                result = [{"affected_rows": cursor.rowcount}]

            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)

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
            "created_at": datetime.utcnow()
        }

        # Build INSERT statement
        table_name = db_info["db_name"]
        columns = ", ".join(data_with_meta.keys())
        placeholders = ", ".join(["%s" for _ in data_with_meta])
        values = tuple(data_with_meta.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return record_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)

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
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO plaid_tokens (id, user_id, access_token, item_id, created_at)
                   VALUES (%s, %s, %s, %s, %s)""",
                (token_id, user_id, access_token, item_id, datetime.utcnow())
            )
            conn.commit()
            return token_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_plaid_token(self, user_id: str) -> Optional[str]:
        """Get Plaid access token for user"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT access_token FROM plaid_tokens WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            row = cursor.fetchone()
            return row["access_token"] if row else None
        finally:
            cursor.close()
            self._release_connection(conn)

    def save_google_token(self, user_id: str, token_data: Dict[str, Any]) -> str:
        """Save Google Calendar token for user"""
        token_id = str(uuid.uuid4())
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            # Upsert - insert or update if exists
            cursor.execute(
                """INSERT INTO google_tokens (id, user_id, token_data, created_at)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (user_id) DO UPDATE SET
                   token_data = EXCLUDED.token_data,
                   created_at = EXCLUDED.created_at""",
                (token_id, user_id, json.dumps(token_data), datetime.utcnow())
            )
            conn.commit()
            return token_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_google_token(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Google Calendar token for user"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT token_data FROM google_tokens WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            return json.loads(row["token_data"]) if row else None
        finally:
            cursor.close()
            self._release_connection(conn)

    def delete_google_token(self, user_id: str) -> bool:
        """Delete Google Calendar token for user"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM google_tokens WHERE user_id = %s",
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            self._release_connection(conn)


# Global instance
db_manager = DatabaseManager()
 
