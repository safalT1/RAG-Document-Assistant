import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import ingest, chat, booking
from app.database.models import Base
from app.database.session import engine

# Logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logging.getLogger(__name__).info("Database tables created.")
    yield


# App 
app = FastAPI(
    title="RAG Document Assistant",
    description=(
        "Backend with Document Ingestion and Conversational RAG APIs. "
        "Uses Qdrant for vector storage, Redis for chat memory, "
        "and SQLite for metadata & interview bookings."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Routers
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(booking.router, prefix="/bookings", tags=["Bookings"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "service": "RAG Document Assistant",
        "docs": "/docs",
    }