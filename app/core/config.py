import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

QDRANT_PATH: str = os.getenv("QDRANT_PATH", "./qdrant_data")
QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "documents")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app_data.db")

LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")