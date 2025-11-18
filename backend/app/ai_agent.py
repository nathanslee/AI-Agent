import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AIAgent:
    """AI Agent for database schema generation, SQL queries, and intelligent suggestions"""

    @staticmethod
    def generate_database_schema(user_description: str) -> Dict[str, Any]:
        """
        Generate database schema from natural language description.

        Args:
            user_description: User's description of what they want to track

        Returns:
            Schema dict with database_name, display_name, and fields
        """
        system_prompt = """You are an expert database architect. Your job is to create SQLite database schemas from natural language descriptions.

Given a user's description of what they want to track, generate a clean, well-structured database schema.

Rules:
1. Generate a snake_case table name (e.g., "grocery_items", "workout_logs")
2. Generate a human-readable display name (e.g., "Grocery Items", "Workout Logs")
3. Include appropriate fields based on what the user wants to track
4. Use SQLite data types: TEXT, INTEGER, REAL
5. Mark fields as optional: true if they should allow NULL
6. Always include common helpful fields like dates, categories, or descriptions
7. Be smart about field types (dates should be TEXT in ISO format, prices should be REAL)
8. Add helpful fields the user might not have explicitly mentioned but would likely need

Output ONLY valid JSON in this exact format:
{
  "database_name": "table_name",
  "display_name": "Display Name",
  "fields": [
    {"name": "field_name", "type": "TEXT", "optional": false},
    {"name": "another_field", "type": "INTEGER", "optional": true}
  ]
}"""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_description}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        schema = json.loads(response.choices[0].message.content)
        return schema

    @staticmethod
    def natural_language_to_sql(
        command: str,
        schema: Dict[str, Any],
        existing_data_sample: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Convert natural language command to SQL query.

        Args:
            command: Natural language command
            schema: Database schema
            existing_data_sample: Sample of existing data for context

        Returns:
            {
                "sql": "SQL query string",
                "operation": "SELECT|INSERT|UPDATE|DELETE",
                "requires_confirmation": bool,
                "explanation": "Human-readable explanation"
            }
        """
        table_name = schema["database_name"]
        fields = schema["fields"]
        fields_description = "\n".join([
            f"- {f['name']} ({f['type']}) {'OPTIONAL' if f.get('optional') else 'REQUIRED'}"
            for f in fields
        ])

        system_prompt = f"""You are an expert SQL query generator. Convert natural language commands into safe, valid SQLite queries.

Database: {table_name}
Fields:
{fields_description}

Rules:
1. Generate valid SQLite syntax
2. Use ISO 8601 date format (YYYY-MM-DD) for dates
3. For INSERT, provide reasonable defaults for missing fields
4. For SELECT, use appropriate WHERE clauses
5. For UPDATE/DELETE, always include a WHERE clause
6. Use TODAY as {datetime.now().strftime('%Y-%m-%d')}
7. Infer values intelligently (e.g., "bought today" means date_bought = TODAY)

Output ONLY valid JSON:
{{
  "sql": "the SQL query",
  "operation": "INSERT|SELECT|UPDATE|DELETE",
  "requires_confirmation": true if destructive,
  "explanation": "what this query does in plain English"
}}"""

        user_message = f"Command: {command}"
        if existing_data_sample:
            user_message += f"\n\nExisting data sample:\n{json.dumps(existing_data_sample[:3], indent=2)}"

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result

    @staticmethod
    def suggest_expiration_date(item_name: str, item_type: Optional[str] = None) -> str:
        """
        Suggest expiration date for a food item.

        Args:
            item_name: Name of the item
            item_type: Category (produce, dairy, etc.)

        Returns:
            ISO date string
        """
        system_prompt = """You are a food safety expert. Given a food item, estimate a reasonable expiration date from TODAY.

Consider:
- Produce: 3-7 days
- Dairy: 5-14 days
- Meat (fresh): 1-3 days
- Frozen items: 30-90 days
- Canned goods: 180-365 days
- Bread: 3-7 days

TODAY is """ + datetime.now().strftime('%Y-%m-%d') + """

Output ONLY valid JSON:
{
  "expiration_date": "YYYY-MM-DD",
  "reasoning": "brief explanation"
}"""

        user_message = f"Item: {item_name}"
        if item_type:
            user_message += f"\nCategory: {item_type}"

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result["expiration_date"]

    @staticmethod
    def categorize_item(item_name: str, available_categories: Optional[List[str]] = None) -> str:
        """
        Automatically categorize an item.

        Args:
            item_name: Name of the item
            available_categories: List of existing categories to choose from

        Returns:
            Category name
        """
        system_prompt = """You are a smart categorization assistant. Given an item name, assign it to the most appropriate category.

Common categories:
- produce (fruits, vegetables)
- dairy (milk, cheese, yogurt)
- meat (chicken, beef, pork, fish)
- pantry (pasta, rice, canned goods)
- bakery (bread, pastries)
- frozen (frozen foods)
- snacks (chips, cookies)
- beverages (drinks)
- other

Output ONLY valid JSON:
{
  "category": "category_name",
  "confidence": "high|medium|low"
}"""

        user_message = f"Item: {item_name}"
        if available_categories:
            user_message += f"\n\nExisting categories to choose from: {', '.join(available_categories)}"

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result["category"]

    @staticmethod
    def map_plaid_transaction_to_schema(
        transaction: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map a Plaid transaction to database schema.

        Args:
            transaction: Plaid transaction object
            schema: Target database schema

        Returns:
            Mapped data ready for insertion
        """
        fields = [f["name"] for f in schema["fields"]]
        fields_description = "\n".join([
            f"- {f['name']} ({f['type']})"
            for f in schema["fields"]
        ])

        system_prompt = f"""You are a data mapping expert. Map a Plaid banking transaction to this database schema.

Database: {schema['database_name']}
Available fields:
{fields_description}

Rules:
1. Map transaction data to appropriate fields
2. Use intelligent mapping (e.g., transaction.name -> item_name, transaction.amount -> amount)
3. Use transaction.date for date fields
4. Extract useful info from transaction.name and transaction.category
5. Set reasonable defaults for unmapped fields
6. Don't include ID or created_at (auto-generated)

Output ONLY valid JSON with field mappings:
{{
  "field_name": "value",
  "another_field": "value"
}}"""

        user_message = f"Plaid Transaction:\n{json.dumps(transaction, indent=2)}"

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result

    @staticmethod
    def suggest_helpful_queries(schema: Dict[str, Any], data_sample: List[Dict]) -> List[Dict[str, str]]:
        """
        Suggest helpful queries the user might want to run.

        Args:
            schema: Database schema
            data_sample: Sample of existing data

        Returns:
            List of suggested queries with descriptions
        """
        system_prompt = f"""You are a helpful data analyst. Given a database schema and sample data, suggest 3-5 useful queries the user might want to run.

Database: {schema['database_name']}

Generate practical queries like:
- Finding items expiring soon
- Grouping by category
- Finding most expensive items
- Date range queries
- Statistics (COUNT, AVG, SUM)

Output ONLY valid JSON:
{{
  "suggestions": [
    {{"description": "Find items expiring this week", "natural_language": "show me items expiring this week"}},
    {{"description": "Group by category", "natural_language": "show me totals by category"}}
  ]
}}"""

        user_message = f"Schema:\n{json.dumps(schema, indent=2)}\n\nSample data:\n{json.dumps(data_sample[:5], indent=2)}"

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        result = json.loads(response.choices[0].message.content)
        return result["suggestions"]


# Global AI agent instance
ai_agent = AIAgent()
