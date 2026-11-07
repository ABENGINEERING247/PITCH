import os, json, re
import streamlit as st

def _client():
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from e
    key = ""
    model = "gpt-6-luna"
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
        model = st.secrets.get("OPENAI_MODEL", model)
    except Exception:
        pass
    key = key or os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", model)
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured. Add it to Streamlit Secrets or environment variables.")
    return OpenAI(api_key=key), model

def _completion(system, user, temperature=0.4):
    client, model = _client()
    response = client.chat.completions.create(
        model=model, temperature=temperature,
        messages=[{"role":"system","content":system},{"role":"user","content":user}]
    )
    return response.choices[0].message.content or ""

def generate_questions(subject, topic, sections, difficulty, bloom, language, mcq_options, reference_text=""):
    schema = """Return ONLY a valid JSON array. Each item must have:
{"type":"MCQ|Short|Long|Fill in the Blanks|True/False|Descriptive|Numerical|Practical",
"question":"question text","options":["..."],"answer":"teacher answer","explanation":"marking guidance","marks":2}
For non-MCQ options use []. Do not wrap JSON in markdown."""
    system = "You are PITCH, an expert assessment designer. Produce accurate, unambiguous, syllabus-aligned assessment questions. Do not fabricate facts from supplied references. When source text is provided, prioritize it."
    user = f"""Create examination questions for subject: {subject}
Topics/syllabus: {topic}
Sections: {json.dumps(sections)}
Difficulty: {difficulty}
Bloom levels: {", ".join(bloom)}
Language: {language}
MCQ options per question: {mcq_options}
Reference material (may be incomplete): {reference_text[:18000]}
Generate exactly the requested count for each section, label each question's type and marks. MCQs must have exactly {mcq_options} options and one correct answer. True/False answers must be True or False. Fill blanks should include an answer. Avoid duplicates.
{schema}"""
    raw = _completion(system, user, 0.3)
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.I|re.M).strip()
    data = json.loads(raw)
    if not isinstance(data, list): raise ValueError("AI did not return a JSON question list.")
    return data

def chat_response(prompt):
    return _completion(
        "You are PITCH AI Assistant, a helpful assessment and teaching-content expert. Help educators design questions, answer keys, rubrics, study notes, lesson summaries and fair assessment criteria. Be clear, structured, and identify uncertainty. Do not claim to have read files unless their text is supplied.",
        prompt, 0.5
    )
