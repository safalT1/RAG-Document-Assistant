import logging
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import DocumentMetadata
from app.services.file_parser import extract_text
from app.services.chunking import chunk_text
from app.services.embedding import get_embeddings
from app.services.vector_store import create_collection, store_embeddings
from app.schemas.response import IngestResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    strategy: Annotated[str, Query(description="Chunking strategy")] = "fixed",
    db: Session = Depends(get_db),
) -> IngestResponse:
   
    if strategy not in ("fixed", "sentence"):
        raise HTTPException(status_code=400, detail="Strategy must be 'fixed' or 'sentence'.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # Determine file type
    file_type = "pdf" if file.filename.endswith(".pdf") else "txt" if file.filename.endswith(".txt") else None
    if file_type is None:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    try:
        # Step 1 — Extract text
        content: bytes = await file.read()
        text: str = extract_text(file.filename, content)

        # Step 2 — Chunk
        chunks = chunk_text(text, strategy)
        if not chunks:
            raise HTTPException(status_code=400, detail="No text content extracted from the file.")

        # Step 3 — Embed
        embeddings = get_embeddings(chunks)

        # Step 4 — Store in Qdrant
        create_collection(vector_size=len(embeddings[0]))
        store_embeddings(chunks, embeddings)

        # Step 5 — Save metadata to SQLite
        metadata = DocumentMetadata(
            filename=file.filename,
            file_type=file_type,
            chunk_strategy=strategy,
            num_chunks=len(chunks),
            embedding_dim=len(embeddings[0]),
        )
        db.add(metadata)
        db.commit()

        logger.info(
            "Ingested '%s': %d chunks, dim=%d, strategy=%s",
            file.filename, len(chunks), len(embeddings[0]), strategy,
        )

        return IngestResponse(
            filename=file.filename,
            file_type=file_type,
            chunk_strategy=strategy,
            num_chunks=len(chunks),
            embedding_dim=len(embeddings[0]),
        )

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Ingestion failed for '%s'", file.filename)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")