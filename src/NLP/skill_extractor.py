import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def resume_text_to_json(resume_text):
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
                        "\"tools\": [], "
                        "\"experience_years\": {\"min\": null, \"max\": null}, "
                        "\"domains\": []"
                        "}"
                )
            },
            {
                "role": "user",
                "content": resume_text
            }
        ],
        temperature=0
    )

    raw = completion.choices[0].message.content.strip()

    # --- SAFE JSON EXTRACTION ---
    start = raw.find("{")
    end = raw.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found:\n{raw}")

    json_str = raw[start:end]

    # --- JSON SANITIZATION ---
    json_str = json_str.replace(",}", "}")
    json_str = json_str.replace(",]", "]")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON returned by model:\n{json_str}"
        ) from e
    

if __name__ == "__main__":

    resume_text = """
    Python Developer with 2 years of experience.
    Worked on machine learning models and data analysis projects.
    Strong in Python, SQL, Git, and TensorFlow.
    """

    jd_data_scientist = """
    We are hiring a Data Scientist.
    Strong Python and SQL.
    Experience with Machine Learning algorithms.
    Data analysis and feature engineering.
    Tools: Git, TensorFlow.
    """

    jd_backend = """
    We are looking for a Backend Engineer.
    Strong Python.
    Experience with REST APIs.
    Django or Flask framework.
    Database knowledge and Docker.
    """

    resume_json = resume_text_to_json(resume_text)
    jd_ds_json = resume_text_to_json(jd_data_scientist)
    jd_backend_json = resume_text_to_json(jd_backend)

    print("RESUME JSON:")
    print(json.dumps(resume_json, indent=2))

    print("\nJD 1 – DATA SCIENTIST JSON:")
    print(json.dumps(jd_ds_json, indent=2))

    print("\nJD 2 – BACKEND ENGINEER JSON:")
    print(json.dumps(jd_backend_json, indent=2))