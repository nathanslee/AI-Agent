from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import os
import csv
import json
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import (
    SignupRequest, LoginRequest, TokenResponse, UserResponse,
    CreateDatabaseRequest, DatabaseResponse,
    ExecuteSQLRequest, NaturalLanguageRequest, InsertDataRequest,
    SuggestExpirationRequest, CategorizeItemRequest,
    ExchangeTokenRequest, SyncTransactionsRequest,
    GenerateSchemaRequest, CreateDatabaseWithSchemaRequest
)
from .auth import hash_password, verify_password, create_access_token, get_current_user_id
from .database import db_manager
from .ai_agent import ai_agent
from .sql_validator import sql_validator
from .plaid_integration import plaid_integration

app = FastAPI(
    title="DataBuddy API",
    description="AI-powered per-user database management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.railway.app",
        "https://*.vercel.app",
        "*"  # For development - restrict this in production!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """Create a new user account"""
    try:
        # Hash password and create user
        hashed_password = hash_password(request.password)
        user_id = db_manager.create_user(request.email, hashed_password)

        # Generate JWT token
        access_token = create_access_token(data={"sub": user_id})

        return TokenResponse(access_token=access_token)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login to existing account"""
    user = db_manager.get_user_by_email(request.email)

    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": user["id"]})

    return TokenResponse(access_token=access_token)


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current user info"""
    user = db_manager.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(**user)


# ============================================================================
# DATABASE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/databases", response_model=List[DatabaseResponse])
async def list_databases(user_id: str = Depends(get_current_user_id)):
    """List all databases for the current user"""
    databases = db_manager.get_user_databases(user_id)
    return [DatabaseResponse(**db) for db in databases]


@app.post("/api/databases/create", response_model=DatabaseResponse)
async def create_database(
    request: CreateDatabaseRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new database from natural language description"""
    try:
        # Use AI to generate schema
        schema = ai_agent.generate_database_schema(request.description)

        # Create the database
        db_id = db_manager.create_user_database(
            user_id=user_id,
            db_name=schema["database_name"],
            display_name=schema["display_name"],
            schema=schema
        )

        # Get the created database
        db_info = db_manager.get_database_by_id(db_id, user_id)

        return DatabaseResponse(
            id=db_info["id"],
            db_name=db_info["db_name"],
            display_name=db_info["display_name"],
            schema=db_info["schema"],
            created_at=db_info["created_at"]
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/databases/create-with-schema", response_model=DatabaseResponse)
async def create_database_with_schema(
    request: CreateDatabaseWithSchemaRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new database from a provided schema"""
    try:
        # Make a mutable copy of the schema
        schema = dict(request.schema)

        # Filter out disabled fields
        enabled_fields = [field for field in schema.get("fields", []) if field.get("enabled", True)]

        # Remove the 'enabled' key from fields
        cleaned_fields = []
        for field in enabled_fields:
            field_copy = dict(field)
            field_copy.pop("enabled", None)
            cleaned_fields.append(field_copy)

        # Update schema with cleaned fields
        schema["fields"] = cleaned_fields

        # Create the database (this will update schema["database_name"] internally)
        db_id = db_manager.create_user_database(
            user_id=user_id,
            db_name=schema["database_name"],
            display_name=schema["display_name"],
            schema=schema
        )

        # Get the created database to return the correct schema
        db_info = db_manager.get_database_by_id(db_id, user_id)

        return DatabaseResponse(
            id=db_info["id"],
            db_name=db_info["db_name"],
            display_name=db_info["display_name"],
            schema=db_info["schema"],
            created_at=db_info["created_at"]
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/api/databases/{db_id}")
async def delete_database(db_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a database"""
    success = db_manager.delete_database(db_id, user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

    return {"message": "Database deleted successfully"}


@app.get("/api/databases/{db_id}")
async def get_database(db_id: str, user_id: str = Depends(get_current_user_id)):
    """Get database details"""
    db_info = db_manager.get_database_by_id(db_id, user_id)

    if not db_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

    return DatabaseResponse(
        id=db_info["id"],
        db_name=db_info["db_name"],
        display_name=db_info["display_name"],
        schema=db_info["schema"],
        created_at=db_info["created_at"]
    )


# ============================================================================
# DATA OPERATION ENDPOINTS
# ============================================================================

@app.get("/api/data/{db_id}")
async def get_all_data(db_id: str, user_id: str = Depends(get_current_user_id)):
    """Get all data from a database"""
    try:
        data = db_manager.get_all_data(db_id, user_id)
        return {"data": data}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/api/data/{db_id}/insert")
async def insert_data(
    db_id: str,
    request: InsertDataRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Insert data via form submission"""
    try:
        record_id = db_manager.insert_data(db_id, user_id, request.data)
        return {"message": "Data inserted successfully", "id": record_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/execute/sql")
async def execute_sql(
    request: ExecuteSQLRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Execute a SQL query (with safety validation)"""
    # Validate SQL for safety
    is_valid, error_message = sql_validator.validate_sql(request.sql)

    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    try:
        result = db_manager.execute_query(request.db_id, user_id, request.sql)
        return {
            "success": True,
            "data": result,
            "operation": sql_validator.extract_operation_type(request.sql)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/execute/natural")
async def execute_natural_language(
    request: NaturalLanguageRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Execute a natural language command"""
    try:
        # Get database schema
        db_info = db_manager.get_database_by_id(request.db_id, user_id)
        if not db_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        print(f"DEBUG: Database schema: {db_info['schema']}")

        # Get sample data for context
        existing_data = db_manager.get_all_data(request.db_id, user_id)

        # Convert to SQL using AI
        sql_result = ai_agent.natural_language_to_sql(
            request.command,
            db_info["schema"],
            existing_data[:5]
        )

        print(f"DEBUG: Generated SQL: {sql_result['sql']}")

        # Validate SQL for safety
        is_valid, error_message = sql_validator.validate_sql(sql_result["sql"])

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Generated unsafe SQL: {error_message}"
            )

        # Execute the query
        result = db_manager.execute_query(request.db_id, user_id, sql_result["sql"])

        return {
            "success": True,
            "sql": sql_result["sql"],
            "explanation": sql_result["explanation"],
            "operation": sql_result["operation"],
            "requires_confirmation": sql_result.get("requires_confirmation", False),
            "data": result
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print(f"ERROR in execute_natural_language: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.get("/api/export/{db_id}/csv")
async def export_csv(db_id: str, user_id: str = Depends(get_current_user_id)):
    """Export database to CSV format"""
    try:
        db_info = db_manager.get_database_by_id(db_id, user_id)
        if not db_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        data = db_manager.get_all_data(db_id, user_id)

        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to export")

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        # Return as streaming response
        output.seek(0)
        filename = f"{db_info['display_name'].replace(' ', '_')}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/api/export/{db_id}/json")
async def export_json(db_id: str, user_id: str = Depends(get_current_user_id)):
    """Export database to JSON format"""
    try:
        db_info = db_manager.get_database_by_id(db_id, user_id)
        if not db_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        data = db_manager.get_all_data(db_id, user_id)

        # Create JSON with metadata
        export_data = {
            "database_name": db_info["display_name"],
            "exported_at": db_info["created_at"],
            "record_count": len(data),
            "records": data
        }

        output = json.dumps(export_data, indent=2, default=str)
        filename = f"{db_info['display_name'].replace(' ', '_')}.json"

        return StreamingResponse(
            iter([output]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/api/export/{db_id}/pdf")
async def export_pdf(db_id: str, user_id: str = Depends(get_current_user_id)):
    """Export database to PDF format"""
    try:
        db_info = db_manager.get_database_by_id(db_id, user_id)
        if not db_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        data = db_manager.get_all_data(db_id, user_id)

        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data to export")

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(f"<b>{db_info['display_name']}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Prepare table data
        headers = list(data[0].keys())
        table_data = [headers]

        for row in data:
            row_values = [str(v)[:50] if v else "" for v in row.values()]  # Truncate long values
            table_data.append(row_values)

        # Create table
        col_widths = [max(70, 700 // len(headers))] * len(headers)
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5CF6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F3FF')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
        ]))
        elements.append(table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        filename = f"{db_info['display_name'].replace(' ', '_')}.pdf"

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# AI SUGGESTION ENDPOINTS
# ============================================================================

@app.post("/api/ai/suggest-expiration")
async def suggest_expiration(
    request: SuggestExpirationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Get AI suggestion for expiration date"""
    try:
        expiration_date = ai_agent.suggest_expiration_date(
            request.item_name,
            request.item_type
        )
        return {"expiration_date": expiration_date}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/ai/categorize")
async def categorize_item(
    request: CategorizeItemRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Get AI suggestion for category"""
    try:
        category = ai_agent.categorize_item(
            request.item_name,
            request.available_categories
        )
        return {"category": category}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/ai/generate-schema")
async def generate_schema(
    request: GenerateSchemaRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate database schema from description without creating database"""
    try:
        schema = ai_agent.generate_database_schema(request.description)
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/api/ai/suggestions/{db_id}")
async def get_query_suggestions(
    db_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get helpful query suggestions"""
    try:
        db_info = db_manager.get_database_by_id(db_id, user_id)
        if not db_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        existing_data = db_manager.get_all_data(db_id, user_id)

        suggestions = ai_agent.suggest_helpful_queries(
            db_info["schema"],
            existing_data
        )

        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# PLAID INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/plaid/create-link-token")
async def create_plaid_link_token(user_id: str = Depends(get_current_user_id)):
    """Create Plaid Link token"""
    try:
        link_token = plaid_integration.create_link_token(user_id)
        return {"link_token": link_token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/plaid/exchange-token")
async def exchange_plaid_token(
    request: ExchangeTokenRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Exchange Plaid public token for access token"""
    try:
        result = plaid_integration.exchange_public_token(request.public_token)

        # Save access token
        db_manager.save_plaid_token(
            user_id,
            result["access_token"],
            result["item_id"]
        )

        return {"message": "Bank connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/plaid/sync-transactions")
async def sync_plaid_transactions(
    request: SyncTransactionsRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Sync Plaid transactions to database"""
    try:
        # Get Plaid access token
        access_token = db_manager.get_plaid_token(user_id)
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No bank connected. Please connect your bank first."
            )

        # Get database info
        db_info = db_manager.get_database_by_id(request.db_id, user_id)
        if not db_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        # Fetch transactions from Plaid
        transactions = plaid_integration.get_transactions(
            access_token,
            request.start_date,
            request.end_date
        )

        # Map and insert each transaction
        inserted_count = 0
        for txn in transactions:
            try:
                # Use AI to map transaction to schema
                mapped_data = ai_agent.map_plaid_transaction_to_schema(
                    txn,
                    db_info["schema"]
                )

                # Insert into database
                db_manager.insert_data(request.db_id, user_id, mapped_data)
                inserted_count += 1
            except Exception as e:
                print(f"Failed to insert transaction {txn.get('transaction_id')}: {e}")
                continue

        return {
            "message": f"Successfully synced {inserted_count} transactions",
            "total_transactions": len(transactions),
            "inserted": inserted_count
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DataBuddy API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
