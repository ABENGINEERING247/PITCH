import streamlit as st
from services.db import init_db, save_paper, list_papers, get_paper, save_question, list_questions, save_result, list_results
from services.ai import generate_questions, chat_response
from services.exports import export_docx, export_pdf, export_xlsx, export_csv, export_results_docx, export_results_pdf, export_results_xlsx
from services.reference import extract_reference
from services.scoring import calculate_result, validate_paper

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

with st.sidebar:
    st.markdown('<div class="pitch-title">PITCH</div><div class="pitch-sub">Professional Intelligent Testing & Content Hub</div>', unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navigation", [
        "Dashboard", "AI Exam Generator", "Question Bank", "AI Assistant",
        "Reference Library", "Answer Key & Marking Scheme", "Scoring & Results",
        "Templates & Branding", "Export Center", "Settings"
    ])
    st.caption("Built for educators, instructors and examination departments.")

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
    else: st.info("No papers yet. Start with AI Exam Generator.")
    st.subheader("Quick start")
    st.write("1. Add reference books or notes.  2. Generate questions.  3. Review and edit.  4. Configure marks and attempts.  5. Export your paper.")

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
        footer_text = st.text_input("Footer (e.g. Confidential – Examination Copy)", "PITCH | Confidential Examination Paper")
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
        language = st.selectbox("Language",["English","Urdu","Bilingual (English + Urdu)"])
        mcq_options = st.selectbox("MCQ options per question",[2,3,4,5,6],index=2)
        include_key = st.checkbox("Generate answer key and marking scheme",True)
        reference_text = st.text_area("Reference content (optional)", help="You can also add files in Reference Library and paste relevant extracted text here.")
        submitted=st.form_submit_button("Generate examination paper with AI",type="primary",use_container_width=True)
    if submitted:
        if not subject.strip(): st.error("Enter a subject name.")
        else:
            with st.spinner("Generating questions with the configured OpenAI model..."):
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
    if "current_paper" in st.session_state:
        paper=st.session_state["current_paper"]
        st.subheader("Review and edit generated questions")
        st.caption("Edit question text, options, marks and answers before exporting.")
        edited=[]
        for n,q in enumerate(paper["questions"]):
            with st.expander(f"{n+1}. [{q.get('type','Question')}] {q.get('question','')[:90]}", expanded=False):
                q["question"]=st.text_area("Question",q.get("question",""),key=f"editq{n}")
                q["marks"]=st.number_input("Marks",0.0,1000.0,float(q.get("marks",1)),step=0.5,key=f"editm{n}")
                if q.get("options"):
                    opts=st.text_area("Options (one per line)", "\n".join(q["options"]),key=f"edito{n}")
                    q["options"]=[x.strip() for x in opts.splitlines() if x.strip()]
                q["answer"]=st.text_area("Answer / key (teacher only)",q.get("answer",""),key=f"edita{n}")
                q["explanation"]=st.text_area("Explanation / marking guidance",q.get("explanation",""),key=f"edite{n}")
            edited.append(q)
        paper["questions"]=edited
        st.session_state["current_paper"]=paper
        if st.button("Save changes to question bank",type="primary"):
            for q in edited: save_question(q, paper["subject"])
            save_paper(paper, st.session_state.get("current_paper_id"))
            st.success("Paper and questions saved.")
        st.subheader("Paper configuration summary")
        st.write(f"Questions incorporated: **{len(edited)}** | Questions to attempt: **{sum(s['attempt'] for s in paper['sections'])}** | Configured paper marks: **{paper['total_marks']}**")
        st.caption("Question marks are individually editable. Confirm section totals and attempt rules before printing.")
        col1,col2,col3,col4=st.columns(4)
        for col,fmt,fn in [(col1,"DOCX",export_docx),(col2,"PDF",export_pdf),(col3,"XLSX",export_xlsx),(col4,"CSV",export_csv)]:
            data=fn(paper)
            mime={"DOCX":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","PDF":"application/pdf","XLSX":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","CSV":"text/csv"}[fmt]
            col.download_button(f"Download {fmt}",data,file_name=f"PITCH_{paper['subject'].replace(' ','_')}.{fmt.lower()}",mime=mime,use_container_width=True)

elif page == "Question Bank":
    header("Question Bank", "Store and reuse questions across examinations.")
    with st.form("manual_question"):
        subject=st.text_input("Subject")
        typ=st.selectbox("Type",["MCQ","Short","Long","Fill in the Blanks","True/False","Descriptive","Numerical","Practical"])
        question=st.text_area("Question")
        options=st.text_area("Options (one per line; for MCQs)")
        answer=st.text_area("Correct answer / model answer")
        marks=st.number_input("Marks",0.5,1000.0,2.0,step=0.5)
        if st.form_submit_button("Save question"):
            if question.strip():
                save_question({"type":typ,"question":question,"options":[x for x in options.splitlines() if x.strip()],"answer":answer,"marks":marks},subject)
                st.success("Question saved.")
            else: st.error("Question text is required.")
    data=list_questions()
    if data: st.dataframe([{"ID":q["id"],"Subject":q["subject"],"Type":q["type"],"Question":q["question"],"Marks":q["marks"]} for q in data],use_container_width=True)

elif page == "AI Assistant":
    header("PITCH AI Assistant", "Ask for exam content, question improvements, explanations, marking rubrics and study material.")
    if "chat" not in st.session_state: st.session_state.chat=[]
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt=st.chat_input("Ask PITCH AI to create or improve examination content...")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try: reply=chat_response(prompt)
                except Exception as ex: reply=f"AI service error: {ex}"
                st.markdown(reply)
        st.session_state.chat.append({"role":"assistant","content":reply})
    if st.button("Clear conversation"): st.session_state.chat=[]; st.rerun()

elif page == "Reference Library":
    header("Reference Library", "Upload textbooks, notes, syllabus documents and images as source material.")
    uploaded=st.file_uploader("Upload reference files",type=["pdf","docx","txt","png","jpg","jpeg"],accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            try:
                content=extract_reference(f.name,f.getvalue())
                st.session_state.setdefault("reference_texts",{})[f.name]=content
                st.success(f"Extracted text from {f.name} ({len(content)} characters).")
                with st.expander(f"Preview: {f.name}"): st.text(content[:12000])
            except Exception as ex: st.error(f"{f.name}: {ex}")
    refs=st.session_state.get("reference_texts",{})
    if refs:
        st.subheader("Available session references")
        for name,content in refs.items(): st.write(f"**{name}** — {len(content)} characters")
        combined="\n\n".join(f"### {k}\n{v}" for k,v in refs.items())
        st.download_button("Download extracted reference text",combined,file_name="PITCH_reference_material.txt")
        st.info("Paste relevant extracted content into the AI Exam Generator's reference field. Files are processed in this session; persistent library storage can be added through a configured institutional deployment.")

elif page == "Answer Key & Marking Scheme":
    header("Answer Key & Marking Scheme", "Create a teacher copy with correct answers, explanations and marking guidance.")
    papers=list_papers()
    if papers:
        selected=st.selectbox("Select paper",papers,format_func=lambda p:f"#{p['id']} — {p['title']}")
        paper=get_paper(selected["id"])
        if paper:
            st.write(f"**{paper['subject']}** — {len(paper['questions'])} questions")
            for n,q in enumerate(paper["questions"],1):
                with st.expander(f"Q{n}: {q.get('question','')[:100]}"):
                    st.write("**Answer:**",q.get("answer","Not provided"))
                    st.write("**Marks:**",q.get("marks",0))
                    st.write("**Marking guidance:**",q.get("explanation",""))
            c1,c2=st.columns(2)
            c1.download_button("Teacher answer key (DOCX)",export_docx(paper,include_answers=True),file_name="PITCH_answer_key.docx")
            c2.download_button("Teacher answer key (PDF)",export_pdf(paper,include_answers=True),file_name="PITCH_answer_key.pdf")
    else: st.info("Generate and save a paper first.")

elif page == "Scoring & Results":
    header("Scoring & Results", "Record student marks and export result sheets.")
    papers=list_papers()
    with st.form("result_form"):
        roll=st.text_input("Roll number")
        student=st.text_input("Student name")
        subject=st.text_input("Subject")
        total=st.number_input("Total marks",1.0,10000.0,100.0)
        obtained=st.number_input("Obtained marks",0.0,10000.0,0.0)
        grade_scale=st.selectbox("Grade scale",["Standard (A+ ≥90, A ≥80, B ≥70, C ≥60, D ≥50)","Pass / Fail"])
        submitted=st.form_submit_button("Calculate and save result")
        if submitted:
            if obtained>total: st.error("Obtained marks cannot exceed total marks.")
            elif not roll.strip(): st.error("Roll number is required.")
            else:
                result=calculate_result(roll,student,subject,obtained,total,grade_scale)
                save_result(result); st.success(f"Saved: {result['percentage']:.2f}% — Grade {result['grade']}")
    results=list_results()
    if results:
        st.subheader("Recorded results")
        st.dataframe(results,use_container_width=True)
        c1,c2,c3=st.columns(3)
        c1.download_button("Results DOCX",export_results_docx(results),file_name="PITCH_results.docx")
        c2.download_button("Results PDF",export_results_pdf(results),file_name="PITCH_results.pdf")
        c3.download_button("Results XLSX",export_results_xlsx(results),file_name="PITCH_results.xlsx")

elif page == "Templates & Branding":
    header("Templates & Branding", "Configure a consistent examination paper identity.")
    with st.form("branding"):
        logo=st.file_uploader("Institution logo",type=["png","jpg","jpeg"])
        institution=st.text_input("Default institution name")
        dept=st.text_input("Default department")
        header_text=st.text_area("Default header")
        footer=st.text_input("Default footer","PITCH | Confidential")
        watermark=st.text_input("Watermark","CONFIDENTIAL")
        page_size=st.selectbox("Page size",["A4","Letter"])
        if st.form_submit_button("Save template settings"):
            st.session_state["branding"]={"institution":institution,"department":dept,"header_text":header_text,"footer_text":footer,"watermark":watermark,"page_size":page_size}
            if logo: st.session_state["branding"]["logo_name"]=logo.name; st.session_state["branding"]["logo_bytes"]=logo.getvalue()
            st.success("Branding saved for this session. Apply these defaults when creating a new paper.")

elif page == "Export Center":
    header("Export Center", "Download saved examination papers and result reports.")
    papers=list_papers()
    if papers:
        selected=st.selectbox("Choose examination",papers,format_func=lambda p:f"#{p['id']} — {p['title']}")
        paper=get_paper(selected["id"])
        if paper:
            st.write(f"{paper['subject']} | {len(paper['questions'])} questions | {paper['total_marks']} marks")
            cols=st.columns(4)
            for col,fmt,fn in zip(cols,["DOCX","PDF","XLSX","CSV"],[export_docx,export_pdf,export_xlsx,export_csv]):
                col.download_button(f"Download {fmt}",fn(paper),file_name=f"PITCH_paper_{selected['id']}.{fmt.lower()}")
    else: st.info("No saved papers available.")

elif page == "Settings":
    header("Settings & API Configuration", "Configure OpenAI securely through Streamlit Secrets or environment variables.")
    st.code('OPENAI_API_KEY = "your-api-key"\nOPENAI_MODEL = "gpt-6-luna"',language="toml")
    st.info("Place these values in .streamlit/secrets.toml locally or in Streamlit Community Cloud → App settings → Secrets. Never commit API keys to GitHub.")
    st.write("Configured model:", st.secrets.get("OPENAI_MODEL","gpt-6-luna") if hasattr(st,"secrets") else "gpt-6-luna")
    st.write("API key detected:", bool((st.secrets.get("OPENAI_API_KEY","") if hasattr(st,"secrets") else "") or __import__("os").getenv("OPENAI_API_KEY")))
    st.warning("The selected model ID must be enabled for your OpenAI API project. If unavailable, change OPENAI_MODEL to a model your account can access.")
    st.markdown("**Privacy:** uploaded references are processed by this app and may be sent to the configured AI provider when used for generation. Do not upload confidential student records or copyrighted material unless authorized.")
