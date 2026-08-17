from pydantic import BaseModel, Field
from typing import Optional, List


class IngestResponse(BaseModel):
  
    file_type: str
    chunk_strategy: str
    num_chunks: int
    embedding_dim: int
    message: str = "Document ingested and stored successfully"


class ChatResponse(BaseModel):
   
    session_id: str
    query: str
    answer: str
    sources: List[str] = Field(default_factory=list, description="Retrieved context chunks")
    booking: Optional[dict] = Field(None, description="Booking info if detected")


class BookingResponse(BaseModel):
   
    id: int
    name: str
    email: str
    date: str
    time: str
    notes: Optional[str] = None
    message: str = "Interview booking created successfully"


class BookingListResponse(BaseModel):
   
    bookings: List[BookingResponse]
