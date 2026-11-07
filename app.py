import streamlit as st
from services.db import init_db, save_paper, list_papers, get_paper, save_question, list_questions, save_result, list_results
from services.ai import generate_questions, chat_response
from services.exports import export_docx, export_pdf, export_xlsx, export_csv, export_results_docx, export_results_pdf, export_results_xlsx
from services.reference import extract_reference
from services.scoring import calculate_result, validate_paper
from services.offline_generator import parse_uploaded_file, generate_offline_questions

st.set_page_config(page_title="PITCH | Examination Hub", page_icon="📝", layout="wide")
init_db()

st.markdown("""
<style>
:root { --pitch:#087f8c; }
.block-container {padding-top:1.5rem; max-width:1500px;}
[data-testid="stSidebar"] {background:#f1f8f8;}
.pitch-title {font-size:2.25rem;font-weight:800;color:#087f8c;letter-spacing:.5px;}
.pitch-sub {color:#52666a;font-size:1rem;}
div.stButton>button[kind="primary"] {background:#087f8c;border-color:#087f8c;}
</style>
""", unsafe_allow_html=True)

# Large Center Popup Modal (Auto-closes after 10 seconds or manually)
st.markdown("""
<div id="pitch-popup" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 999999; background: white; border-top: 6px solid #087f8c; padding: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); border-radius: 12px; width: 600px; max-width: 90vw; font-family: sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
        <h2 style="margin: 0; color: #087f8c; font-size: 1.4rem; font-weight: 800; line-height: 1.3;">PITCH – Professional Intelligent Testing & Content Hub</h2>
        <button onclick="document.getElementById('pitch-popup').style.display='none'" style="background: #f1f8f8; border: none; font-size: 1.5rem; cursor: pointer; color: #52666a; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; line-height: 1;">&times;</button>
    </div>
    <p style="margin: 0 0 15px 0; font-size: 0.95rem; color: #52666a; line-height: 1.5;">AI-assisted examination paper generation, question bank, reference material processing, answer keys, scoring and result exports.</p>
    <div style="font-size: 0.88rem; color: #333; max-height: 250px; overflow-y: auto; padding-right: 5px;">
        <strong style="color: #087f8c; font-size: 1rem;">Features:</strong>
        <ul style="margin: 6px 0 0 18px; padding: 0; line-height: 1.6;">
            <li>Generate MCQs, short/long, fill-in-the-blank, true/false, descriptive, numerical and practical questions.</li>
            <li>Configure section counts, marks per question, attempt counts, difficulty, Bloom taxonomy, language and MCQ option count.</li>
            <li>Customize institution, department, exam header, instructions and footer.</li>
            <li>AI chatbot for examination and teaching content.</li>
            <li>Upload PDF, DOCX, TXT and images (image OCR requires Tesseract).</li>
            <li>SQLite question bank, saved papers and student results.</li>
            <li>Export examination papers and answer keys to DOCX/PDF/XLSX/CSV; results to DOCX/PDF/XLSX.</li>
        </ul>
    </div>
    <div style="margin-top: 20px; text-align: right;">
        <button onclick="document.getElementById('pitch-popup').style.display='none'" style="background: #087f8c; color: white; border: none; padding: 8px 20px; font-size: 0.9rem; border-radius: 6px; cursor: pointer; font-weight: 600;">Got it</button>
    </div>
    <script>
        setTimeout(function() {
            var popup = document.getElementById('pitch-popup');
            if (popup) { popup.style.display = 'none'; }
        }, 10000);
    </script>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="pitch-title">PITCH</div><div class="pitch-sub">Professional Intelligent Testing Hub</div>', unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigation", [
        "Dashboard", "AI Exam Generator", "Offline Exam Generator", "Question Bank", "AI Assistant",
        "Reference Library", "Answer Key & Marking Scheme", "Scoring & Results",
        "Templates & Branding", "Export Center", "Settings"
    ])
    st.caption("Developed by Engr. Bilal Mehmood")

def header(title, desc=""):
    st.markdown(f"# {title}")
    if desc: st.caption(desc)

if page == "Dashboard":
    header("PITCH Dashboard", "Create, manage, assess and export examinations from one workspace.")
    papers = list_papers()
    qs = list_questions()
    results = list_results()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Saved papers", len(papers))
    c2.metric("Question bank", len(qs))
    c3.metric("Recorded results", len(results))
    c4.metric("Export formats", "4")
    st.subheader("Recent examination papers")
    if papers:
        st.dataframe([{"ID":p["id"],"Title":p["title"],"Subject":p["subject"],"Date":p["created_at"]} for p in papers[:10]], use_container_width=True)
    else: st.info("No papers yet. Start with AI Exam Generator or Offline Exam Generator.")

elif page == "AI Exam Generator":
    header("AI Examination Paper Generator", "Build a complete, customizable paper with section rules, marks and internal choices.")
    with st.form("paper_form"):
        a,b,c = st.columns(3)
        institution = a.text_input("Institution / University", "PITCH Examination Centre")
        department = b.text_input("Department", "Department")
        exam_type = c.selectbox("Examination type", ["Midterm","Final","Quiz","Class Test","Practical","Entry Test","Other"])
        d,e,f = st.columns(3)
        subject = d.text_input("Subject name", "General Subject")
        code = e.text_input("Subject code")
        class_name = f.text_input("Class / Semester")
        g,h,i = st.columns(3)
        academic_year = g.text_input("Academic year")
        exam_date = h.text_input("Examination date")
        duration = i.text_input("Time allowed", "2 Hours")
        total_marks = st.number_input("Total paper marks", min_value=1, max_value=1000, value=100)
        instructions = st.text_area("General instructions", "Attempt the required number of questions. Write answers clearly.")
        header_text = st.text_area("Custom header (optional)")
        footer_text = st.text_input("Footer", "PITCH | Confidential Examination Paper")
        
        st.markdown("### Section configuration")
        section_count = st.number_input("Number of sections", 1, 8, 3)
        sections=[]
        for idx in range(int(section_count)):
            st.markdown(f"**Section {chr(65+idx)}**")
            x1,x2,x3,x4 = st.columns(4)
            typ=x1.selectbox("Question type", ["MCQ","Short","Long","Fill in the Blanks","True/False","Descriptive","Numerical","Practical"], key=f"typ{idx}")
            count=x2.number_input("Questions generated",1,100,5,key=f"cnt{idx}")
            marks=x3.number_input("Marks each",0.5,1000.0,2.0,key=f"mrk{idx}",step=0.5)
            attempt=x4.number_input("Attempt",1,int(count),int(count),key=f"att{idx}")
            sections.append({"name":f"Section {chr(65+idx)}","type":typ,"count":int(count),"marks":float(marks),"attempt":int(attempt)})
            
        topic = st.text_area("Topics / syllabus / learning outcomes")
        difficulty = st.select_slider("Difficulty", options=["Very Easy","Easy","Moderate","Difficult","Advanced"], value="Moderate")
        bloom = st.multiselect("Bloom's taxonomy",["Remember","Understand","Apply","Analyze","Evaluate","Create"],default=["Remember","Understand","Apply"])
        language = st.selectbox("Language",["English","Urdu","Bilingual"])
        mcq_options = st.selectbox("MCQ options per question",[2,3,4,5,6],index=2)
        include_key = st.checkbox("Generate answer key and marking scheme",True)
        reference_text = st.text_area("Reference content (optional)")
        submitted=st.form_submit_button("Generate examination paper with AI",type="primary",use_container_width=True)
        
    if submitted:
        if not subject.strip(): st.error("Enter a subject name.")
        else:
            with st.spinner("Generating questions..."):
                try:
                    qs=generate_questions(subject, topic, sections, difficulty, bloom, language, mcq_options, reference_text)
                    paper={"institution":institution,"department":department,"exam_type":exam_type,"subject":subject,"code":code,"class_name":class_name,"academic_year":academic_year,"exam_date":exam_date,"duration":duration,"total_marks":float(total_marks),"instructions":instructions,"header_text":header_text,"footer_text":footer_text,"sections":sections,"questions":qs,"include_key":include_key}
                    issues=validate_paper(paper)
                    pid=save_paper(paper)
                    st.session_state["current_paper"]=paper
                    st.session_state["current_paper_id"]=pid
                    st.success(f"Generated {len(qs)} questions. Saved paper #{pid}.")
                    for issue in issues: st.warning(issue)
                except Exception as ex: st.error(f"Generation failed: {ex}")

elif page == "Offline Exam Generator":
    header("Offline Paper Generator (PDF, DOCX, XLSX, CSV)", "Generate examination papers locally using uploaded documents without requiring an internet connection.")
    
    with st.form("offline_form"):
        uploaded_doc = st.file_uploader("Upload Source File (PDF, DOCX, XLSX, CSV)", type=["pdf", "docx", "xlsx", "csv"])
        
        a,b,c = st.columns(3)
        institution = a.text_input("Institution / University", "PITCH Offline Centre", key="off_inst")
        department = b.text_input("Department", "Department", key="off_dept")
        subject = c.text_input("Subject name", "Document Assessment", key="off_subj")
        
        d,e,f = st.columns(3)
        exam_type = d.selectbox("Examination type", ["Midterm","Final","Quiz","Class Test","Assignment"], key="off_type")
        duration = e.text_input("Time allowed", "1.5 Hours", key="off_dur")
        total_marks = f.number_input("Total paper marks", min_value=1, max_value=1000, value=50, key="off_tot")
        
        instructions = st.text_area("General instructions", "Answer all questions based on the uploaded reference document.", key="off_instru")
        
        st.markdown("### Section configuration")
        section_count = st.number_input("Number of sections", 1, 5, 2, key="off_sec_cnt")
        sections=[]
        for idx in range(int(section_count)):
            st.markdown(f"**Section {chr(65+idx)}**")
            x1,x2,x3,x4 = st.columns(4)
            typ = x1.selectbox("Question type", ["MCQ","Short","Descriptive","True/False"], key=f"off_typ{idx}")
            count = x2.number_input("Questions generated", 1, 50, 5, key=f"off_cnt{idx}")
            marks = x3.number_input("Marks each", 0.5, 100.0, 2.0, key=f"off_mrk{idx}", step=0.5)
            attempt = x4.number_input("Attempt", 1, int(count), int(count), key=f"off_att{idx}")
            sections.append({"name": f"Section {chr(65+idx)}", "type": typ, "count": int(count), "marks": float(marks), "attempt": int(attempt)})
            
        offline_submitted = st.form_submit_button("Generate Paper Offline", type="primary", use_container_width=True)

    if offline_submitted:
        if not uploaded_doc:
            st.error("Please upload a PDF, DOCX, XLSX, or CSV file to build questions offline.")
        elif not subject.strip():
            st.error("Please enter a subject name.")
        else:
            with st.spinner("Extracting content and parsing questions locally..."):
                try:
                    extracted_text = parse_uploaded_file(uploaded_doc)
                    qs = generate_offline_questions(extracted_text, sections)
                    paper = {
                        "institution": institution,
                        "department": department,
                        "exam_type": exam_type,
                        "subject": subject,
                        "code": "OFF-101",
                        "class_name": "General",
                        "academic_year": "2026",
                        "exam_date": "Today",
                        "duration": duration,
                        "total_marks": float(total_marks),
                        "instructions": instructions,
                        "header_text": f"Offline Generated from: {uploaded_doc.name}",
                        "footer_text": "PITCH | Offline Document Examination",
                        "sections": sections,
                        "questions": qs,
                        "include_key": True
                    }
                    
                    pid = save_paper(paper)
                    st.session_state["current_paper"] = paper
                    st.session_state["current_paper_id"] = pid
                    st.success(f"Successfully generated {len(qs)} offline questions from '{uploaded_doc.name}'! Saved as paper #{pid}.")
                except Exception as ex:
                    st.error(f"Offline generation failed: {ex}")

    if "current_paper" in st.session_state and page == "Offline Exam Generator":
        paper = st.session_state["current_paper"]
        st.subheader("Review Offline Generated Questions")
        edited = []
        for n, q in enumerate(paper["questions"]):
            with st.expander(f"{n+1}. [{q.get('type','Question')}] {q.get('question','')[:90]}", expanded=False):
                q["question"] = st.text_area("Question", q.get("question",""), key=f"off_editq{n}")
                q["marks"] = st.number_input("Marks", 0.0, 100.0, float(q.get("marks",1)), step=0.5, key=f"off_editm{n}")
                if q.get("options"):
                    opts = st.text_area("Options (one per line)", "\n".join(q["options"]), key=f"off_edito{n}")
                    q["options"] = [x.strip() for x in opts.splitlines() if x.strip()]
                q["answer"] = st.text_area("Answer / key", q.get("answer",""), key=f"off_edita{n}")
            edited.append(q)
        paper["questions"] = edited
        
        col1, col2, col3, col4 = st.columns(4)
        for col, fmt, fn in [(col1,"DOCX",export_docx),(col2,"PDF",export_pdf),(col3,"XLSX",export_xlsx),(col4,"CSV",export_csv)]:
            data = fn(paper)
            mime = {"DOCX":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","PDF":"application/pdf","XLSX":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","CSV":"text/csv"}[fmt]
            col.download_button(f"Download {fmt}", data, file_name=f"Offline_Paper.{fmt.lower()}", mime=mime, use_container_width=True)

elif page == "Question Bank":
    header("Question Bank", "Store and reuse questions across examinations.")
    data = list_questions()
    if data: st.dataframe([{"ID":q["id"],"Subject":q["subject"],"Type":q["type"],"Question":q["question"],"Marks":q["marks"]} for q in data],use_container_width=True)
    else: st.info("Question bank is empty.")

elif page == "AI Assistant":
    header("PITCH AI Assistant", "Ask for exam content, question improvements, explanations, marking rubrics and study material.")
    if "chat" not in st.session_state: st.session_state.chat=[]
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt = st.chat_input("Ask PITCH AI...")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            reply = chat_response(prompt)
            st.markdown(reply)
        st.session_state.chat.append({"role":"assistant","content":reply})

elif page == "Reference Library":
    header("Reference Library", "Upload textbooks, notes, syllabus documents and images as source material.")
    uploaded = st.file_uploader("Upload reference files", type=["pdf","docx","txt","png","jpg","jpeg"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            content = extract_reference(f.name, f.getvalue())
            st.session_state.setdefault("reference_texts", {})[f.name] = content
            st.success(f"Extracted text from {f.name} ({len(content)} characters).")

elif page == "Answer Key & Marking Scheme":
    header("Answer Key & Marking Scheme", "Create a teacher copy with correct answers, explanations and marking guidance.")
    papers = list_papers()
    if papers:
        selected = st.selectbox("Select paper", papers, format_func=lambda p:f"#{p['id']} — {p['title']}")
        paper = get_paper(selected["id"])
        if paper:
            for n, q in enumerate(paper["questions"], 1):
                st.write(f"**Q{n}:** {q.get('question')} | **Answer:** `{q.get('answer')}`")
            c1, c2 = st.columns(2)
            c1.download_button("Teacher answer key (DOCX)", export_docx(paper, include_answers=True), file_name="PITCH_answer_key.docx")
            c2.download_button("Teacher answer key (PDF)", export_pdf(paper, include_answers=True), file_name="PITCH_answer_key.pdf")

elif page == "Scoring & Results":
    header("Scoring & Results", "Record student marks and export result sheets.")
    with st.form("result_form"):
        roll = st.text_input("Roll number")
        student = st.text_input("Student name")
        subject = st.text_input("Subject")
        total = st.number_input("Total marks", 1.0, 10000.0, 100.0)
        obtained = st.number_input("Obtained marks", 0.0, 10000.0, 0.0)
        grade_scale = st.selectbox("Grade scale", ["Standard (A+ ≥90, A ≥80, B ≥70, C ≥60, D ≥50)", "Pass / Fail"])
        submitted = st.form_submit_button("Calculate and save result")
        if submitted:
            result = calculate_result(roll, student, subject, obtained, total, grade_scale)
            save_result(result)
            st.success(f"Saved: {result['percentage']:.2f}% — Grade {result['grade']}")
    results = list_results()
    if results:
        st.dataframe(results, use_container_width=True)

elif page == "Templates & Branding":
    header("Templates & Branding", "Configure examination paper identity.")
    st.info("Branding settings applied successfully for the current session.")

elif page == "Export Center":
    header("Export Center", "Download saved examination papers and result reports.")
    papers = list_papers()
    if papers:
        selected = st.selectbox("Choose examination", papers, format_func=lambda p:f"#{p['id']} — {p['title']}")
        paper = get_paper(selected["id"])
        if paper:
            cols = st.columns(4)
            for col, fmt, fn in zip(cols, ["DOCX","PDF","XLSX","CSV"],[export_docx,export_pdf,export_xlsx,export_csv]):
                col.download_button(f"Download {fmt}", fn(paper), file_name=f"PITCH_paper_{selected['id']}.{fmt.lower()}")

elif page == "Settings":
    header("Settings & API Configuration", "Configure OpenAI securely.")
    st.code('OPENAI_API_KEY = "your-api-key"', language="toml")
