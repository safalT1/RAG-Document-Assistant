from typing import List

def fixed_chunk(text: str, chunk_size: int = 300) -> List[str]:
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def sentence_chunk(text: str) -> List[str]:
    sentences = text.split(".")
    chunks = [s.strip() for s in sentences if s.strip()]
    return chunks

def chunk_text(text: str, strategy: str) -> List[str]:
    if strategy == "fixed":
        return fixed_chunk(text)

    elif strategy == "sentence":
        return sentence_chunk(text)

    else:
        raise ValueError("Invalid chunking strategy")