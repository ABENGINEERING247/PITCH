from io import BytesIO, StringIO
import csv

def _rows(paper, include_answers=False):
    rows=[]
    for i,q in enumerate(paper.get("questions",[]),1):
        rows.append({"No.":i,"Section":q.get("section",""),"Type":q.get("type",""),"Question":q.get("question",""),
        "Options":" | ".join(q.get("options",[]) or []),"Marks":q.get("marks",0),
        "Answer":q.get("answer","") if include_answers else "",
        "Explanation / Marking guide":q.get("explanation","") if include_answers else ""})
    return rows

def export_docx(paper, include_answers=False):
    from docx import Document
    from docx.shared import Inches, Pt
    d=Document()
    sec=d.sections[0]; sec.top_margin=Inches(.65); sec.bottom_margin=Inches(.65)
    if paper.get("header_text"): d.add_paragraph(paper["header_text"])
    p=d.add_paragraph(); p.alignment=1
    r=p.add_run(paper.get("institution","")); r.bold=True; r.font.size=Pt(15)
    p=d.add_paragraph(); p.alignment=1
    r=p.add_run(paper.get("department","")); r.bold=True
    p=d.add_paragraph(); p.alignment=1
    r=p.add_run(paper.get("exam_type","Examination")); r.bold=True; r.font.size=Pt(13)
    d.add_paragraph(f"Subject: {paper.get('subject','')}    Code: {paper.get('code','')}    Class/Semester: {paper.get('class_name','')}")
    d.add_paragraph(f"Date: {paper.get('exam_date','')}    Time: {paper.get('duration','')}    Total Marks: {paper.get('total_marks','')}")
    d.add_paragraph("Student Name: ______________________________    Roll No: __________________")
    d.add_heading("Instructions",level=2); d.add_paragraph(paper.get("instructions",""))
    if include_answers: d.add_heading("TEACHER COPY – ANSWERS & MARKING SCHEME",level=1)
    for idx,q in enumerate(paper.get("questions",[]),1):
        p=d.add_paragraph()
        p.add_run(f"Q{idx}. ").bold=True
        p.add_run(q.get("question",""))
        p.add_run(f"  [{q.get('marks',0)} marks]").bold=True
        for j,opt in enumerate(q.get("options",[]) or []):
            d.add_paragraph(f"{chr(65+j)}. {opt}",style="List Bullet")
        if include_answers:
            d.add_paragraph(f"Answer: {q.get('answer','')}")
            if q.get("explanation"): d.add_paragraph(f"Marking guidance: {q['explanation']}")
    for s in d.sections:
        if paper.get("footer_text"): s.footer.paragraphs[0].text=paper["footer_text"]
    out=BytesIO(); d.save(out); return out.getvalue()

def export_pdf(paper, include_answers=False):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
    from xml.sax.saxutils import escape
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
    styles=getSampleStyleSheet(); story=[]
    story += [Paragraph(escape(paper.get("institution","")),styles["Title"]),Paragraph(escape(paper.get("department","")),styles["Heading2"]),
              Paragraph(escape(paper.get("exam_type","Examination")),styles["Heading2"]),
              Paragraph(f"Subject: {escape(paper.get('subject',''))} | Code: {escape(paper.get('code',''))}",styles["Normal"]),
              Paragraph(f"Class: {escape(paper.get('class_name',''))} | Date: {escape(paper.get('exam_date',''))} | Time: {escape(paper.get('duration',''))}",styles["Normal"]),
              Paragraph(f"Total Marks: {escape(str(paper.get('total_marks','')))}",styles["Normal"]),
              Spacer(1,8),Paragraph("Student Name: ____________________________   Roll No: ______________",styles["Normal"]),
              Paragraph("Instructions",styles["Heading2"]),Paragraph(escape(paper.get("instructions","")),styles["BodyText"]),Spacer(1,8)]
    if include_answers: story.append(Paragraph("TEACHER COPY – ANSWERS & MARKING SCHEME",styles["Heading1"]))
    for i,q in enumerate(paper.get("questions",[]),1):
        block=[Paragraph(f"<b>Q{i}.</b> {escape(q.get('question',''))} <b>[{escape(str(q.get('marks',0)))} marks]</b>",styles["BodyText"])]
        for j,opt in enumerate(q.get("options",[]) or []):
            block.append(Paragraph(f"{chr(65+j)}. {escape(opt)}",styles["BodyText"]))
        if include_answers:
            block.append(Paragraph(f"<b>Answer:</b> {escape(q.get('answer',''))}",styles["BodyText"]))
            if q.get("explanation"): block.append(Paragraph(f"<b>Marking guidance:</b> {escape(q['explanation'])}",styles["BodyText"]))
        block.append(Spacer(1,7)); story.append(KeepTogether(block))
    def footer(canvas, doc_):
        canvas.saveState(); canvas.setFont("Helvetica",8)
        canvas.drawString(18*mm,10*mm,paper.get("footer_text","PITCH"))
        canvas.drawRightString(A4[0]-18*mm,10*mm,f"Page {doc_.page}")
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); return out.getvalue()

def export_xlsx(paper):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb=Workbook(); ws=wb.active; ws.title="Questions"
    ws.append(["PITCH Examination Paper"]); ws.append(["Institution",paper.get("institution","")]); ws.append(["Subject",paper.get("subject","")])
    ws.append(["Total Marks",paper.get("total_marks",0)]); ws.append([])
    headers=list(_rows(paper)[0].keys()) if paper.get("questions") else ["No.","Type","Question","Options","Marks","Answer","Explanation / Marking guide"]
    ws.append(headers)
    for row in _rows(paper): ws.append([row.get(h,"") for h in headers])
    for cell in ws[1]+ws[6]:
        cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="087F8C")
    for col in ws.columns:
        letter=col[0].column_letter; ws.column_dimensions[letter].width=min(55,max(14,max(len(str(c.value or "")) for c in col)+2))
    out=BytesIO(); wb.save(out); return out.getvalue()

def export_csv(paper):
    out=StringIO(); rows=_rows(paper)
    fields=list(rows[0].keys()) if rows else ["No.","Type","Question","Options","Marks","Answer","Explanation / Marking guide"]
    w=csv.DictWriter(out,fieldnames=fields); w.writeheader(); w.writerows(rows)
    return out.getvalue().encode("utf-8-sig")

def export_results_xlsx(results):
    from openpyxl import Workbook
    wb=Workbook(); ws=wb.active; ws.title="Results"
    headers=list(results[0].keys()) if results else ["roll_no","student","subject","obtained","total","percentage","grade","status"]
    ws.append(headers)
    for r in results: ws.append([r.get(h,"") for h in headers])
    out=BytesIO(); wb.save(out); return out.getvalue()

def export_results_docx(results):
    from docx import Document
    d=Document(); d.add_heading("PITCH – Examination Results",0)
    t=d.add_table(rows=1,cols=8); t.style="Table Grid"
    headers=["Roll No","Student","Subject","Obtained","Total","%","Grade","Status"]
    for c,h in zip(t.rows[0].cells,headers): c.text=h
    for r in results:
        for c,v in zip(t.add_row().cells,[r["roll_no"],r["student"],r["subject"],r["obtained"],r["total"],r["percentage"],r["grade"],r["status"]]): c.text=str(v)
    out=BytesIO(); d.save(out); return out.getvalue()

def export_results_pdf(results):
    from reportlab.lib.pagesizes import landscape,A4
    from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph
    from reportlab.lib import colors
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=landscape(A4))
    data=[["Roll No","Student","Subject","Obtained","Total","%","Grade","Status"]]
    data += [[str(r[k]) for k in ["roll_no","student","subject","obtained","total","percentage","grade","status"]] for r in results]
    table=Table(data,repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#087F8C")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.5,colors.grey),("FONTSIZE",(0,0),(-1,-1),8)]))
    doc.build([Paragraph("PITCH – Examination Results",__import__("reportlab.lib.styles",fromlist=["getSampleStyleSheet"]).getSampleStyleSheet()["Title"]),table])
    return out.getvalue()
