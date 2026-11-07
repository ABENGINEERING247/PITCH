import io
import csv
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl

def get_alignment_enum(align_str):
    if align_str == "Right":
        return WD_ALIGN_PARAGRAPH.RIGHT
    elif align_str == "Center":
        return WD_ALIGN_PARAGRAPH.CENTER
    return WD_ALIGN_PARAGRAPH.LEFT

def export_docx(paper, include_answers=False):
    doc = Document()
    
    # Layout and Branding Configurations
    branding = paper.get("branding", {})
    logo_bytes = branding.get("logo_bytes")
    align_str = branding.get("alignment", "Center")
    docx_align = get_alignment_enum(align_str)
    
    # Add Logo if present
    if logo_bytes:
        p_logo = doc.add_paragraph()
        p_logo.alignment = docx_align
        try:
            p_logo.add_run().add_picture(io.BytesIO(logo_bytes), width=docx.shared.Inches(1.2))
        except Exception:
            pass

    # Header / Institution Title
    p_inst = doc.add_paragraph()
    p_inst.alignment = docx_align
    p_inst.add_run(paper.get("institution", "Examination Centre")).bold = True
    
    p_dept = doc.add_paragraph()
    p_dept.alignment = docx_align
    p_dept.add_run(paper.get("department", "Department"))
    
    doc.add_heading(f"Subject: {paper.get('subject')} ({paper.get('exam_type', 'Exam')})", level=2)
    doc.add_paragraph(f"Time Allowed: {paper.get('duration')} | Total Marks: {paper.get('total_marks')}")
    doc.add_paragraph(f"Instructions: {paper.get('instructions')}")
    doc.add_paragraph("-" * 50)
    
    for idx, q in enumerate(paper.get("questions", []), 1):
        doc.add_paragraph(f"Q{idx}: {q.get('question')} [{q.get('marks')} Marks]")
        if q.get("options"):
            for opt in q["options"]:
                doc.add_paragraph(f"   {opt}")
        if include_answers:
            doc.add_paragraph(f"   [Model Answer]: {q.get('answer')}")
            
    # Bottom Footer
    footer_text = paper.get("footer_text", "PITCH | Confidential Examination Paper")
    section = doc.sections[0]
    footer = section.footer
    f_para = footer.paragraphs[0]
    f_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f_para.text = footer_text
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

def export_pdf(paper, include_answers=False):
    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=letter)
    width, height = letter
    y = height - 40
    
    branding = paper.get("branding", {})
    align_str = branding.get("alignment", "Center")
    
    # Header positioning based on alignment
    c.setFont("Helvetica-Bold", 14)
    inst_text = paper.get("institution", "Examination Centre")
    if align_str == "Right":
        c.drawRightString(width - 50, y, inst_text)
    elif align_str == "Center":
        c.drawCentredString(width / 2.0, y, inst_text)
    else:
        c.drawString(50, y, inst_text)
        
    y -= 20
    c.setFont("Helvetica", 10)
    sub_text = f"Subject: {paper.get('subject')} | Total Marks: {paper.get('total_marks')}"
    if align_str == "Right":
        c.drawRightString(width - 50, y, sub_text)
    elif align_str == "Center":
        c.drawCentredString(width / 2.0, y, sub_text)
    else:
        c.drawString(50, y, sub_text)
        
    y -= 30
    c.line(50, y, width - 50, y)
    y -= 25
    
    for idx, q in enumerate(paper.get("questions", []), 1):
        if y < 80:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, f"Q{idx}: ({q.get('marks')} Marks)")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(70, y, q.get('question')[:90])
        y -= 20
        if include_answers:
            c.drawString(90, y, f"Ans: {str(q.get('answer'))[:85]}")
            y -= 20
            
    # Bottom Footer
    c.setFont("Helvetica-Oblique", 8)
    footer_text = paper.get("footer_text", "PITCH | Confidential Examination Paper")
    c.drawCentredString(width / 2.0, 30, footer_text)
    
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
