
def process_resumes():
    resumes = []
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith('.pdf') and not file.lower().startswith('jd'):
            pdf_path = os.path.join(INPUT_DIR, file)
            text = extract_text_from_pdf(pdf_path)
            cleaned = clean_text(text)
            try:
                resume_json = extract_resume_json(cleaned)
                resumes.append(resume_json)
                # Save each resume JSON to output
                out_name = os.path.splitext(file)[0] + ".json"
                out_path = os.path.join(OUTPUT_DIR, out_name)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(resume_json, f, indent=2)
            except Exception as e:
                print(f"Failed to extract resume from {file}: {e}")
    return resumes

def process_jd():
    for file in os.listdir(INPUT_DIR):
        if file.lower().startswith('jd') and file.lower().endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, file)
            text = extract_text_from_pdf(pdf_path)
            cleaned = clean_text(text)
            try:
                jd_json = extract_jd_json(cleaned)
                # Save JD JSON to output as jd.json
                out_path = os.path.join(OUTPUT_DIR, "jd.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(jd_json, f, indent=2)
                return jd_json
            except Exception as e:
                print(f"Failed to extract JD from {file}: {e}")
    return None

import os
import json
from dotenv import load_dotenv
from groq import Groq
import fitz  # PyMuPDF

# ================== SETUP ==================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# RESUME_DIR = os.path.join(INPUT_DIR, "resumes")
# JD_FILE = os.path.join(INPUT_DIR, "jd.pdf")


# ================== DYNAMIC INPUT PATHS ==================
def get_resume_files():
    return [
        os.path.join(INPUT_DIR, f)
        for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".pdf") and not f.lower().startswith("jd")
    ]

def get_jd_file():
    for f in os.listdir(INPUT_DIR):
        if f.lower().startswith("jd") and f.lower().endswith(".pdf"):
            return os.path.join(INPUT_DIR, f)
    return None

# ================== PDF TEXT EXTRACTION ==================
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    file_name = os.path.basename(pdf_path)

    extracted_text = [f"FILE NAME: {file_name}"]

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text("text").strip()
        if page_text:
            extracted_text.append(f"PAGE {page_num}")
            extracted_text.append(page_text)

    final_text = "\n".join(extracted_text)

    if len(final_text.strip()) < 50:
        print(f"⚠️ Warning: Very little text extracted from {file_name}")

    return final_text

# ================== LIGHT PREPROCESSING ==================
def clean_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = " ".join(lines)
    return " ".join(cleaned.split())

# ================== SAFE JSON PARSER ==================
def safe_json_extract(raw):
    start = raw.find("{")
    end = raw.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError(f"No JSON found:\n{raw}")

    json_str = raw[start:end]
    json_str = json_str.replace(",}", "}").replace(",]", "]")
    return json.loads(json_str)

# ================== RESUME JSON EXTRACTION ==================
def extract_resume_json(text):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert technical recruiter and ATS engine.\n\n"
                    "TASK:\n"
                    "1. Understand the candidate's DOMAIN (e.g., Data Science, Full Stack, Backend, ML).\n"
                    "2. Convert resume descriptions into CANONICAL TECHNICAL SKILLS.\n\n"
                    "STRICT RULES:\n"
                    "- Skills MUST be concrete technologies only (languages, libraries, frameworks).\n"
                    "- DO NOT include responsibilities or soft skills.\n"
                    "- Normalize synonyms:\n"
                    "  • 'EDA', 'data analysis' → Data Analysis\n"
                    "  • 'ML models', 'predictive models' → Machine Learning\n"
                    "  • 'CNN, RNN, LSTM' → Deep Learning\n"
                    "- Group skills logically.\n\n"
                    "Return ONLY valid JSON using this schema:\n"
                    "{\n"
                    "  \"name\": \"\",\n"
                    "  \"email\": \"\",\n"
                    "  \"domain\": \"\",\n"
                    "  \"skills\": [],\n"
                    "  \"tools\": [],\n"
                    "  \"education\": \"\",\n"
                    "  \"experience_years\": 0\n"
                    "}"
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.1
    )

    raw = completion.choices[0].message.content.strip()
    return safe_json_extract(raw)

# ================== JD JSON EXTRACTION ==================
def extract_jd_json(text):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior hiring manager and ATS system.\n\n"
                    "TASK:\n"
                    "1. Identify the PRIMARY DOMAIN of the job role.\n"
                    "2. Infer REQUIRED TECHNICAL SKILLS even if indirectly mentioned.\n"
                    "3. Normalize all skills into CANONICAL TECHNOLOGY TERMS.\n\n"
                    "IMPORTANT RULES:\n"
                    "- Skills must be ONLY languages, libraries, frameworks, databases, or platforms.\n"
                    "- Do NOT include responsibilities, verbs, or soft skills.\n"
                    "- Infer skills from context:\n"
                    "  • 'build ML models' → Machine Learning, Scikit-learn\n"
                    "  • 'analyze datasets' → Data Analysis, Pandas\n"
                    "  • 'deep learning' → TensorFlow, PyTorch\n"
                    "- Prefer INDUSTRY-STANDARD names.\n\n"
                    "Return ONLY valid JSON using this schema:\n"
                    "{\n"
                    "  \"name\": \"\",\n"
                    "  \"domain\": \"\",\n"
                    "  \"skills\": [],\n"
                    "  \"tools\": [],\n"
                    "  \"education\": \"\",\n"
                    "  \"experience_years\": 0,\n"
                    "  \"keywords\": []\n"
                    "}"
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.1
    )

    raw = completion.choices[0].message.content.strip()
    return safe_json_extract(raw)