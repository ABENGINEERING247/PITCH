import os
import json
import streamlit as st

def get_openai_client():
    api_key = ""
    try:
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY", "")
    
    from openai import OpenAI
    return OpenAI(api_key=api_key) if api_key else None

def generate_questions(subject, topic, sections, difficulty, bloom, language, mcq_options, reference_text):
    client = get_openai_client()
    
    if not client:
        qs = []
        for sec in sections:
            for i in range(sec["count"]):
                t = sec["type"]
                q_dict = {
                    "type": t,
                    "question": f"[{subject}] Sample {t} question #{i+1} covering: {topic or 'General Curriculum'}.",
                    "marks": sec["marks"],
                    "answer": "Model answer and grading guidance.",
                    "explanation": f"Evaluates {difficulty} level understanding."
                }
                if t == "MCQ":
                    q_dict["options"] = [f"Option {chr(65+j)}" for j in range(mcq_options)]
                    q_dict["answer"] = "Option A"
                elif t == "True/False":
                    q_dict["options"] = ["True", "False"]
                    q_dict["answer"] = "True"
                qs.append(q_dict)
        return qs

    model = "gpt-6-luna"
    try:
        if hasattr(st, "secrets") and "OPENAI_MODEL" in st.secrets:
            model = st.secrets["OPENAI_MODEL"]
    except Exception:
        pass

    prompt = f"""
    Generate an examination paper for Subject: {subject}.
    Topic/Syllabus: {topic}
    Difficulty: {difficulty}
    Bloom's Taxonomy: {', '.join(bloom)}
    Language: {language}
    Reference Material: {reference_text}
    
    Sections configuration: {json.dumps(sections)}
    MCQ options count: {mcq_options}
    
    Return ONLY a valid JSON array of question objects. Each object must have keys:
    "type", "question", "options" (list of strings if MCQ/True-False else empty list), "answer", "marks", "explanation".
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert academic assessment generator. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=1.0
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    return json.loads(content)

def chat_response(prompt):
    client = get_openai_client()
    if not client:
        return "AI Assistant is running in offline mode. Configure OPENAI_API_KEY in secrets to enable live responses."
    
    model = "gpt-6-luna"
    try:
        if hasattr(st, "secrets") and "OPENAI_MODEL" in st.secrets:
            model = st.secrets["OPENAI_MODEL"]
    except Exception:
        pass
        
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )
    return res.choices[0].message.content
