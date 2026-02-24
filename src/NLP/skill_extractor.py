
import os
import json
from dotenv import load_dotenv
from groq import Groq

# ---------------- SETUP ----------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_DIR = "../../data"
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

RESUME_FILE = os.path.join(INPUT_DIR, "resume1.txt")
JD_FILE = os.path.join(INPUT_DIR, "jd.txt")

# ---------------- FILE READER ----------------
def read_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ---------------- LLM JSON EXTRACTION ----------------
def extract_structured_json(text):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator.\n"
                    "Return ONLY valid JSON.\n"
                    "Rules:\n"
                    "- All keys must be in double quotes\n"
                    "- No trailing commas\n"
                    "- No comments\n"
                    "- No explanation text\n\n"
                    "Schema:\n"
                    "{"
                    "\"name\": \"\", "
                    "\"email\": \"\", "
                    "\"skills\": [], "
                    "\"tools\": [], "
                    "\"education\": \"\", "
                    "\"experience_years\": 0"
                    "}"
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    raw = completion.choices[0].message.content.strip()

    # ---- SAFE JSON EXTRACTION ----
    start, end = raw.find("{"), raw.rfind("}") + 1
    if start == -1 or end == -1:
        raise ValueError(f"No JSON found:\n{raw}")

    json_str = raw[start:end].replace(",}", "}").replace(",]", "]")
    return json.loads(json_str)

def extract_jd_json(text):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator.\n"
                    "Return ONLY valid JSON.\n"
                    "Rules:\n"
                    "- All keys must be in double quotes\n"
                    "- No trailing commas\n"
                    "- No comments\n"
                    "- No explanation text\n\n"
                    "Schema:\n"
                    "{"
                    "\"skills\": [], "
                    "\"min_experience_years\": 0, "
                    "\"keywords\": []"
                    "}"
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    raw = completion.choices[0].message.content.strip()
    start, end = raw.find("{"), raw.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError(f"No JSON found:\n{raw}")

    json_str = raw[start:end].replace(",}", "}").replace(",]", "]")
    return json.loads(json_str)
# ---------------- PROCESSORS ----------------
def process_resume():
    text = read_text_file(RESUME_FILE)
    data = extract_structured_json(text)

    out_path = os.path.join(OUTPUT_DIR, "resume.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data

def process_jd():
    text = read_text_file(JD_FILE)
    data = extract_jd_json(text)

    out_path = os.path.join(OUTPUT_DIR, "jd.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ JD saved at:", os.path.abspath(out_path))
    return data

# ---------------- RUN ----------------
if __name__ == "__main__":
    resume_json = process_resume()
    jd_json = process_jd()           # new format

    print("RESUME JSON:")
    print(json.dumps(resume_json, indent=2))

    print("\nJD JSON:")
    print(json.dumps(jd_json, indent=2))