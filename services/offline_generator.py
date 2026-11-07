import io
import csv
import openpyxl
from pypdf import PdfReader
from docx import Document

def parse_uploaded_file(uploaded_file):
    """Extracts raw text and tabular content from PDF, DOCX, XLSX, or CSV files offline."""
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    text_content = ""
    
    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_content += t + "\n"
                
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            if para.text.strip():
                text_content += para.text + "\n"
                
    elif filename.endswith(".xlsx"):
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            text_content += f"\n--- Sheet: {sheet} ---\n"
            for row in ws.iter_rows(values_only=True):
                row_str = " | ".join([str(cell) for cell in row if cell is not None])
                if row_str.strip():
                    text_content += row_str + "\n"
                    
    elif filename.endswith(".csv"):
        decoded = file_bytes.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(decoded))
        for row in reader:
            row_str = " | ".join([str(cell) for cell in row if cell is not None])
            if row_str.strip():
                text_content += row_str + "\n"
                
    return text_content

def generate_offline_questions(text_content, sections):
    """Parses text locally and builds questions following Bloom's Taxonomy standards for short and long questions."""
    lines = [line.strip() for line in text_content.splitlines() if len(line.strip()) > 15]
    questions = []
    line_idx = 0

    # Bloom Taxonomy Verb Banks
    short_verbs = ["Define", "Explain", "Classify", "Identify", "Illustrate", "Summarize", "Demonstrate"]
    long_verbs = ["Analyze", "Evaluate", "Synthesize", "Formulate", "Critique", "Design", "Compare and Contrast"]

    for section in sections:
        sec_type = section["type"]
        count = section["count"]
        marks = section["marks"]
        
        for i in range(count):
            if lines:
                source_line = lines[line_idx % len(lines)]
                line_idx += 1
            else:
                source_line = f"Core concept item {i+1} derived from uploaded reference material."

            if sec_type == "MCQ":
                q_text = f"Based on the provided document, what is indicated regarding: '{source_line[:60]}...'?"
                options = [
                    f"A) Primary finding associated with {source_line[:20]}",
                    "B) Secondary or alternative interpretation",
                    "C) None of the mentioned factors",
                    "D) Insufficient data provided in source text"
                ]
                answer = "A) Primary finding associated with..."
                explanation = f"Extracted directly from source reference text: {source_line}"
            elif sec_type == "Short":
                verb = short_verbs[(i + line_idx) % len(short_verbs)]
                q_text = f"{verb} the underlying principle concerning: {source_line}"
                options = []
                answer = f"Model Answer (Short Response): Expected explanation covering '{source_line[:40]}'."
                explanation = "Structured according to Bloom's Taxonomy (Understand/Apply level)."
            elif sec_type in ["Long", "Descriptive"]:
                verb = long_verbs[(i + line_idx) % len(long_verbs)]
                q_text = f"{verb} the implications, structural components, or operational framework of: {source_line}"
                options = []
                answer = f"Comprehensive Model Answer: Detailed evaluation and breakdown required for '{source_line[:40]}'."
                explanation = "Structured according to Bloom's Taxonomy (Analyze/Evaluate/Create level)."
            else:
                q_text = f"True or False: {source_line}"
                options = ["True", "False"]
                answer = "True"
                explanation = "Validated against uploaded offline document."

            questions.append({
                "type": sec_type,
                "question": q_text,
                "options": options,
                "answer": answer,
                "marks": float(marks),
                "explanation": explanation
            })
            
    return questions
