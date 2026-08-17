from PyPDF2 import PdfReader


def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def parse_pdf(file_bytes: bytes) -> str:
    from io import BytesIO

    pdf = PdfReader(BytesIO(file_bytes))
    text = ""

    for page in pdf.pages:
        text += page.extract_text() or ""

    return text


def extract_text(filename: str, file_bytes: bytes) -> str:
    if filename.endswith(".txt"):
        return parse_txt(file_bytes)

    elif filename.endswith(".pdf"):
        return parse_pdf(file_bytes)

    else:
        raise ValueError("Unsupported file type")