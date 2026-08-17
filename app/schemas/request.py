from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
   
    session_id: str = Field(..., description="Unique session ID for multi-turn chat")
    query: str = Field(..., min_length=1, description="User question or message")


class BookingRequest(BaseModel):
    
    name: str = Field(..., min_length=1, description="Candidate full name")
    email: str = Field(..., description="Candidate email address")
    date: str = Field(..., description="Interview date in YYYY-MM-DD format")
    time: str = Field(..., description="Interview time in HH:MM format")
    notes: Optional[str] = Field(None, description="Optional notes")
