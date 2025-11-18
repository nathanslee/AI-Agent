from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

from .models import (
    SignupRequest, LoginRequest, TokenResponse, UserResponse,
    CreateDatabaseRequest, DatabaseResponse,
    ExecuteSQLRequest, NaturalLanguageRequest, InsertDataRequest,
    SuggestExpirationRequest, CategorizeItemRequest,
    ExchangeTokenRequest, SyncTransactionsRequest
)
from .auth import hash_password, verify_password, create_access_token, get_current_user_id
from .database import db_manager
from .ai_agent import ai_agent
from .sql_validator import sql_validator
from .plaid_integration import plaid_integration

app = FastAPI(
    title="AI Database Assistant API",
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

        # Get sample data for context
        existing_data = db_manager.get_all_data(request.db_id, user_id)

        # Convert to SQL using AI
        sql_result = ai_agent.natural_language_to_sql(
            request.command,
            db_info["schema"],
            existing_data[:5]
        )

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
        "service": "AI Database Assistant API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
