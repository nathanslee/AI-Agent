from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional

# Auth models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str

# Database models
class CreateDatabaseRequest(BaseModel):
    description: str

class GenerateSchemaRequest(BaseModel):
    description: str

class CreateDatabaseWithSchemaRequest(BaseModel):
    schema: Dict[str, Any]

class DatabaseSchema(BaseModel):
    database_name: str
    display_name: str
    fields: List[Dict[str, Any]]

class DatabaseResponse(BaseModel):
    id: str
    db_name: str
    display_name: str
    schema: Dict[str, Any]
    created_at: str

# Data operation models
class ExecuteSQLRequest(BaseModel):
    db_id: str
    sql: str

class NaturalLanguageRequest(BaseModel):
    db_id: str
    command: str

class InsertDataRequest(BaseModel):
    db_id: str
    data: Dict[str, Any]

# AI suggestion models
class SuggestExpirationRequest(BaseModel):
    item_name: str
    item_type: Optional[str] = None

class CategorizeItemRequest(BaseModel):
    item_name: str
    available_categories: Optional[List[str]] = None

# Plaid models
class ExchangeTokenRequest(BaseModel):
    public_token: str

class SyncTransactionsRequest(BaseModel):
    db_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# Google Calendar models
class GoogleAuthCallbackRequest(BaseModel):
    code: str
    state: str

class CreateCalendarEventRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    start_date: str
    end_date: Optional[str] = None
    all_day: bool = True
    reminder_minutes: int = 1440

class CreateExpirationReminderRequest(BaseModel):
    item_name: str
    expiration_date: str
    days_before: int = 1
