import re
from typing import Tuple, List

class SQLValidator:
    """Validates SQL queries for safety"""

    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        r'\bDROP\s+TABLE\b',
        r'\bDROP\s+DATABASE\b',
        r'\bTRUNCATE\b',
        r'\bALTER\s+TABLE\b',
        r'\bDELETE\s+FROM\s+\w+\s*$',  # DELETE without WHERE
        r'\bDELETE\s+FROM\s+\w+\s*;',  # DELETE without WHERE (with semicolon)
    ]

    # Allow only these SQL operations
    ALLOWED_OPERATIONS = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']

    @staticmethod
    def validate_sql(sql: str) -> Tuple[bool, str]:
        """
        Validate SQL query for safety.

        Returns:
            (is_valid, error_message)
        """
        sql_upper = sql.strip().upper()

        # Check for multiple statements (semicolon injection)
        if sql.count(';') > 1 or (';' in sql and not sql.strip().endswith(';')):
            return False, "Multiple SQL statements are not allowed"

        # Check for dangerous keywords
        for pattern in SQLValidator.DANGEROUS_KEYWORDS:
            if re.search(pattern, sql_upper):
                return False, f"Dangerous SQL operation detected: {pattern}"

        # Check if operation is allowed
        first_word = sql_upper.split()[0] if sql_upper.split() else ""
        if first_word not in SQLValidator.ALLOWED_OPERATIONS:
            return False, f"SQL operation '{first_word}' is not allowed"

        # Special check: DELETE must have WHERE clause
        if first_word == 'DELETE':
            if 'WHERE' not in sql_upper:
                return False, "DELETE queries must include a WHERE clause for safety"

        return True, ""

    @staticmethod
    def is_destructive_operation(sql: str) -> bool:
        """Check if SQL operation is destructive (DELETE, UPDATE)"""
        sql_upper = sql.strip().upper()
        first_word = sql_upper.split()[0] if sql_upper.split() else ""
        return first_word in ['DELETE', 'UPDATE']

    @staticmethod
    def sanitize_table_name(name: str) -> str:
        """Sanitize table name to prevent SQL injection"""
        # Allow only alphanumeric and underscores
        return re.sub(r'[^a-zA-Z0-9_]', '', name)

    @staticmethod
    def sanitize_column_name(name: str) -> str:
        """Sanitize column name to prevent SQL injection"""
        # Allow only alphanumeric and underscores
        return re.sub(r'[^a-zA-Z0-9_]', '', name)

    @staticmethod
    def extract_operation_type(sql: str) -> str:
        """Extract the SQL operation type (SELECT, INSERT, etc.)"""
        sql_upper = sql.strip().upper()
        first_word = sql_upper.split()[0] if sql_upper.split() else ""
        return first_word


# Global validator instance
sql_validator = SQLValidator()
