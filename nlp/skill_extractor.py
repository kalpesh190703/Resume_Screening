
import os
import json
from dotenv import load_dotenv
from groq import Groq
import fitz  # PyMuPDF

# ================== SETUP ==================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_DIR = "../../data"
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# RESUME_DIR = os.path.join(INPUT_DIR, "resumes")
# JD_FILE = os.path.join(INPUT_DIR, "jd.pdf")

# ================== HARD-CODED INPUT PATHS ==================

RESUME_FILES = [
    r"C:\Users\ashis\Downloads\Kalpesh_new.pdf",
    r"C:\Users\ashis\Downloads\Ashish Rajendra Khedkar 5.pdf",
    r"C:\Users\ashis\Downloads\Shashank_Resume_2026.pdf"
   
]

JD_FILE = r"C:\Users\ashis\Downloads\Document.pdf"

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
                    "You are a strict JSON extractor.\n"
                    "Return ONLY the JSON object defined below.\n"
                    "If data is missing, use empty string, empty list, or 0.\n\n"
                    "{\n"
                    "  \"name\": \"\",\n"
                    "  \"email\": \"\",\n"
                    "  \"skills\": [],\n"
                    "  \"tools\": [],\n"
                    "  \"education\": \"\",\n"
                    "  \"experience_years\": 0\n"
                    "}"
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0
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
                    "Return ONLY valid JSON.\n"
                    "{"
                    "\"name\": \"\", "
                    "\"email\": \"\", "
                    "\"skills\": [], "
                    "\"tools\": [], "
                    "\"education\": \"\", "
                    "\"experience_years\": 0, "
                    "\"keywords\": []"
                    "}"
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    raw = completion.choices[0].message.content.strip()
    return safe_json_extract(raw)

#used when particular folder is used for resumes and jd
# ================== PROCESS MULTIPLE RESUMES ==================
# def process_resumes():
#     resumes = []

#     for file in os.listdir(RESUME_DIR):
#         if not file.lower().endswith(".pdf"):
#             continue

#         pdf_path = os.path.join(RESUME_DIR, file)
#         print(f"📄 Processing resume: {file}")

#         raw_text = extract_text_from_pdf(pdf_path)
#         cleaned_text = clean_text(raw_text)
#         data = extract_resume_json(cleaned_text)

#         output_name = file.replace(".pdf", ".json")
#         out_path = os.path.join(OUTPUT_DIR, output_name)

#         with open(out_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=2)

#         resumes.append(data)
#         print(f"✅ Saved: {output_name}")

#     return resumes

#used when hard coded paths are used for resumes and jd

def process_resumes():
    resumes = []

    for pdf_path in RESUME_FILES:
        if not pdf_path.lower().endswith(".pdf"):
            continue

        file = os.path.basename(pdf_path)
        print(f"📄 Processing resume: {file}")

        raw_text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_text(raw_text)
        data = extract_resume_json(cleaned_text)

        output_name = file.replace(".pdf", ".json")
        out_path = os.path.join(OUTPUT_DIR, output_name)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        resumes.append(data)
        print(f"✅ Saved: {output_name}")

    return resumes
# ================== PROCESS JD ==================
def process_jd():
    raw_text = extract_text_from_pdf(JD_FILE)
    cleaned_text = clean_text(raw_text)
    data = extract_jd_json(cleaned_text)

    out_path = os.path.join(OUTPUT_DIR, "jd.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ JD saved at:", os.path.abspath(out_path))
    return data

# ================== RUN ==================
if __name__ == "__main__":
    jd_json = process_jd()
    resume_jsons = process_resumes()

    print(f"\n🎯 Processed {len(resume_jsons)} resumes successfully.")