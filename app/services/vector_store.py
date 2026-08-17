import uuid
import logging
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
)

from app.core.config import QDRANT_PATH, QDRANT_COLLECTION

logger = logging.getLogger(__name__)


client = QdrantClient(path=QDRANT_PATH)

COLLECTION_NAME: str = QDRANT_COLLECTION


def _collection_exists() -> bool:
   
    try:
        collections = client.get_collections().collections
        return any(c.name == COLLECTION_NAME for c in collections)
    except Exception:
        return False


def create_collection(vector_size: int) -> None:
   
    if _collection_exists():
        logger.info("Collection '%s' already exists — deleting it to isolate new document.", COLLECTION_NAME)
        client.delete_collection(collection_name=COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )
    logger.info("Created collection '%s' (dim=%d).", COLLECTION_NAME, vector_size)


def store_embeddings(chunks: List[str], embeddings: List[List[float]]) -> None:
  
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk},
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    logger.info("Stored %d points in '%s'.", len(points), COLLECTION_NAME)


def search(query_embedding: List[float], limit: int = 3) -> List[str]:
 
    if not _collection_exists():
        logger.warning("Collection '%s' does not exist yet. Returning empty results.", COLLECTION_NAME)
        return []

    try:
        # Query more points to allow deduplication
        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit * 3,
        )

        extracted: List[str] = []
        seen = set()
        for point in result.points:
            if point.payload and "text" in point.payload:
                text = point.payload["text"]
                if text not in seen:
                    seen.add(text)
                    extracted.append(text)
                    if len(extracted) == limit:
                        break

        return extracted
    except Exception as exc:
        logger.error("Qdrant search failed: %s", exc)
        return []