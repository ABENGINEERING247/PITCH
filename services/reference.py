import io
from pypdf import PdfReader
from docx import Document

def extract_reference(filename, file_bytes):
    fn = filename.lower()
    text = ""
    if fn.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    elif fn.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        for p in doc.paragraphs:
            if p.text.strip(): text += p.text + "\n"
    elif fn.endswith((".txt", ".csv")):
        text = file_bytes.decode("utf-8", errors="ignore")
    elif fn.endswith((".png", ".jpg", ".jpeg")):
        text = f"[Image uploaded: {filename}. Visual content can be analyzed in AI assistant.]"
    return text
