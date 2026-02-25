# import os
# import json
# from dotenv import load_dotenv
# from groq import Groq

# # ---------------- SETUP ----------------
# load_dotenv()
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# BASE_DIR = "../../data"
# INPUT_DIR = os.path.join(BASE_DIR, "input")
# OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# RESUME_FILE = os.path.join(INPUT_DIR, "resume1.txt")
# JD_FILE = os.path.join(INPUT_DIR, "jd.txt")



# import fitz  # PyMuPDF
# import os

# def extract_text_from_pdf(pdf_path):
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"PDF not found: {pdf_path}")

#     doc = fitz.open(pdf_path)
#     file_name = os.path.basename(pdf_path)

#     extracted_text = []
#     extracted_text.append(f"--- FILE NAME: {file_name} ---\n")

#     for page_num, page in enumerate(doc, start=1):
#         page_text = page.get_text("text").strip()
#         if page_text:
#             extracted_text.append(f"\n--- PAGE {page_num} ---\n")
#             extracted_text.append(page_text)

#     final_text = "\n".join(extracted_text)

#     if len(final_text.strip()) < 50:
#         print("⚠️ Warning: Very little text extracted (might be scanned PDF)")

#     return final_text

# # ---------------- LLM JSON EXTRACTION ----------------
# def extract_structured_json(text):
#     completion = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a strict JSON generator.\n"
#                     "Return ONLY valid JSON.\n"
#                     "Rules:\n"
#                     "- All keys must be in double quotes\n"
#                     "- No trailing commas\n"
#                     "- No comments\n"
#                     "- No explanation text\n\n"
#                     "Schema:\n"
#                     "{"
#                     "\"name\": \"\", "
#                     "\"email\": \"\", "
#                     "\"skills\": [], "
#                     "\"tools\": [], "
#                     "\"education\": \"\", "
#                     "\"experience_years\": 0"
#                     "}"
#                 )
#             },
#             {"role": "user", "content": text}
#         ],
#         temperature=0
#     )

#     raw = completion.choices[0].message.content.strip()

#     # ---- SAFE JSON EXTRACTION ----
#     start, end = raw.find("{"), raw.rfind("}") + 1
#     if start == -1 or end == -1:
#         raise ValueError(f"No JSON found:\n{raw}")

#     json_str = raw[start:end].replace(",}", "}").replace(",]", "]")
#     return json.loads(json_str)

# def extract_jd_json(text):
#     completion = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a strict JSON generator.\n"
#                     "Return ONLY valid JSON.\n"
#                     "Rules:\n"
#                     "- All keys must be in double quotes\n"
#                     "- No trailing commas\n"
#                     "- No comments\n"
#                     "- No explanation text\n\n"
#                     "Schema:\n"
#                     "{"
#                     "\"name\": \"\", "
#                     "\"email\": \"\", "
#                     "\"skills\": [], "
#                     "\"tools\": [], "
#                     "\"education\": \"\", "
#                     "\"experience_years\": 0, "
#                     "\"keywords\": []"
#                     "}"
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": text
#             }
#         ],
#         temperature=0
#     )

#     raw = completion.choices[0].message.content.strip()

#     # ---- SAFE JSON EXTRACTION ----
#     start = raw.find("{")
#     end = raw.rfind("}") + 1

#     if start == -1 or end == -1:
#         raise ValueError(f"No JSON found:\n{raw}")

#     json_str = raw[start:end]
#     json_str = json_str.replace(",}", "}").replace(",]", "]")

#     return json.loads(json_str)
# # ---------------- PROCESSORS ----------------
# def process_resume():
#     text = read_text_file(RESUME_FILE)
#     data = extract_structured_json(text)

#     out_path = os.path.join(OUTPUT_DIR, "resume.json")
#     with open(out_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)

#     return data

# def process_jd():
#     text = read_text_file(JD_FILE)
#     data = extract_jd_json(text)

#     out_path = os.path.join(OUTPUT_DIR, "jd.json")
#     with open(out_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)

#     print("✅ JD saved at:", os.path.abspath(out_path))
#     return data

# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     resume_json = process_resume()
#     jd_json = process_jd()           # new format

#     print("RESUME JSON:")
#     print(json.dumps(resume_json, indent=2))

#     print("\nJD JSON:")
#     print(json.dumps(jd_json, indent=2))