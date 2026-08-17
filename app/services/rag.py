import logging
from typing import Dict, Optional, List

from app.services.embedding import get_embeddings
from app.services.vector_store import search
from app.services.llm import generate_answer, detect_booking_intent
from app.services import chat_memory

logger = logging.getLogger(__name__)


def rag_pipeline(
    session_id: str,
    query: str,
) -> Dict:
   
    history: List[Dict[str, str]] = chat_memory.get_history(session_id)

    # Embed the query
    query_embedding: List[float] = get_embeddings([query])[0]

    # Retrieve relevant chunks from Qdrant
    retrieved_chunks: List[str] = search(query_embedding, limit=5)
    context: str = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant documents found."

    # Generate answer (custom RAG — no RetrievalQAChain)
    answer: str = generate_answer(
        context=context,
        query=query,
        chat_history=history,
    )

    # Check if the exchange contains a booking request
    booking: Optional[Dict] = detect_booking_intent(query, answer)

    # Save both user & assistant messages to memory
    chat_memory.add_message(session_id, role="user", content=query)
    chat_memory.add_message(session_id, role="assistant", content=answer)

    return {
        "answer": answer,
        "sources": retrieved_chunks,
        "booking": booking,
    }