from io import BytesIO
from pathlib import Path

def extract_reference(filename, data):
    ext=Path(filename).suffix.lower()
    if ext==".pdf":
        import fitz
        doc=fitz.open(stream=data,filetype="pdf")
        return "\n\n".join(page.get_text() for page in doc)
    if ext==".docx":
        from docx import Document
        doc=Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext==".txt":
        return data.decode("utf-8",errors="replace")
    if ext in [".png",".jpg",".jpeg"]:
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(BytesIO(data)))
        except Exception as e:
            raise RuntimeError("Image OCR requires Tesseract installed on the host. Try uploading a searchable PDF or text document.") from e
    raise ValueError("Unsupported file type.")
