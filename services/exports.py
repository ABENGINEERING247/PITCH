import io
import csv
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

def export_docx(paper, include_answers=False):
    doc = Document()
    doc.add_heading(paper.get("institution", "Examination Centre"), level=1)
    doc.add_paragraph(f"Subject: {paper.get('subject')} | Type: {paper.get('exam_type')} | Total Marks: {paper.get('total_marks')}")
    doc.add_paragraph(f"Instructions: {paper.get('instructions')}")
    doc.add_paragraph("-" * 40)
    
    for idx, q in enumerate(paper.get("questions", []), 1):
        doc.add_paragraph(f"Q{idx}: {q.get('question')} ({q.get('marks')} Marks)")
        if q.get("options"):
            for opt in q["options"]:
                doc.add_paragraph(f"   {opt}")
        if include_answers:
            doc.add_paragraph(f"   [Answer]: {q.get('answer')}")
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

def export_pdf(paper, include_answers=False):
    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=letter)
    width, height = letter
    y = height - 50
    
    c.drawString(50, y, f"Institution: {paper.get('institution')}")
    y -= 20
    c.drawString(50, y, f"Subject: {paper.get('subject')} | Marks: {paper.get('total_marks')}")
    y -= 30
    
    for idx, q in enumerate(paper.get("questions", []), 1):
        if y < 100:
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"Q{idx}: {q.get('question')[:80]} ({q.get('marks')}M)")
        y -= 20
        if include_answers:
            c.drawString(70, y, f"Ans: {str(q.get('answer'))[:80]}")
            y -= 20
            
    c.save()
    bio.seek(0)
    return bio.getvalue()

def export_xlsx(paper):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Exam Paper"
    ws.append(["Q#", "Type", "Question", "Options", "Answer", "Marks"])
    for idx, q in enumerate(paper.get("questions", []), 1):
        ws.append([idx, q.get("type"), q.get("question"), " | ".join(q.get("options", [])), str(q.get("answer")), q.get("marks")])
    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio.getvalue()

def export_csv(paper):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Q#", "Type", "Question", "Answer", "Marks"])
    for idx, q in enumerate(paper.get("questions", []), 1):
        writer.writerow([idx, q.get("type"), q.get("question"), q.get("answer"), q.get("marks")])
    return output.getvalue().encode("utf-8")

def export_results_docx(results):
    doc = Document()
    doc.add_heading("Examination Results Report", level=1)
    for r in results:
        doc.add_paragraph(f"Roll: {r['roll']} | Student: {r['student']} | Subject: {r['subject']} | Score: {r['obtained']}/{r['total']} ({r['percentage']:.1f}%) | Grade: {r['grade']}")
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

def export_results_pdf(results):
    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=letter)
    width, height = letter
    y = height - 50
    c.drawString(50, y, "Examination Results Report")
    y -= 30
    for r in results:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"{r['roll']} - {r['student']}: {r['obtained']}/{r['total']} ({r['grade']})")
        y -= 20
    c.save()
    bio.seek(0)
    return bio.getvalue()

def export_results_xlsx(results):
    df = pd.DataFrame(results)
    bio = io.BytesIO()
    df.to_excel(bio, index=False)
    bio.seek(0)
    return bio.getvalue()
