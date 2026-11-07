# PITCH – Professional Intelligent Testing & Content Hub

AI-assisted examination paper generation, question bank, reference material processing, answer keys, scoring and result exports.

## Features
- Generate MCQs, short/long, fill-in-the-blank, true/false, descriptive, numerical and practical questions.
- Configure section counts, marks per question, attempt counts, difficulty, Bloom taxonomy, language and MCQ option count.
- Customize institution, department, exam header, instructions and footer.
- AI chatbot for examination and teaching content.
- Upload PDF, DOCX, TXT and images (image OCR requires Tesseract).
- SQLite question bank, saved papers and student results.
- Export examination papers and answer keys to DOCX/PDF/XLSX/CSV; results to DOCX/PDF/XLSX.

## Local installation
1. Install Python 3.10 or newer.
2. Extract the ZIP and open a terminal in the project folder.
3. Create and activate a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - Linux/macOS: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install: `pip install -r requirements.txt`
5. Create `.streamlit/secrets.toml` using `.streamlit/secrets.toml.example`.
6. Add your OpenAI API key and an API model ID enabled for your project.
7. Run: `streamlit run app.py`

## OpenAI configuration
```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-6-luna"
```
The model ID is configurable. `gpt-6-luna` is the requested default placeholder and must be confirmed as available in your OpenAI API account. If it is not enabled, replace it with a model ID available to your project. Do not commit secrets to GitHub.

## Streamlit Community Cloud
- Push the project to a GitHub repository.
- Create a Streamlit Community Cloud app pointing to `app.py`.
- Add `OPENAI_API_KEY` and `OPENAI_MODEL` in App settings → Secrets.
- Deploy.

## Important operational notes
- Review AI-generated questions, answers, difficulty and marks before an official examination.
- The current reference upload processing keeps extracted text in the active app session. The SQLite database stores papers, questions and result records locally. For multi-user production deployment, use managed persistent storage, authentication, role-based access, backups and institution-approved data governance.
- OCR requires Tesseract installed on the host; `packages.txt` requests it on supported Streamlit Linux deployments.
- PDF extraction works best with searchable PDFs. Scanned PDFs may require OCR preprocessing.
- Current scoring records total/obtained marks and calculates grades. Per-question student answer capture, automated subjective grading, moderation and audit trails are planned extensions, not represented as fully implemented functionality in this starter release.
- The app does not execute uploaded files. Only extracted text is passed to AI generation when supplied.
