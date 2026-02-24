import os
import json
from dotenv import load_dotenv
from groq import Groq

# ================== ENV SETUP ==================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")

client = Groq(api_key=GROQ_API_KEY)

THRESHOLD_SCORE = 70.0


# ================== SAFE JSON PARSER ==================
def safe_json_extract(raw_response: str) -> dict:
    """
    Safely extract JSON object from LLM raw response.
    """
    start = raw_response.find("{")
    end = raw_response.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError(f"No valid JSON found in response:\n{raw_response}")

    json_str = raw_response[start:end]
    json_str = json_str.replace(",}", "}").replace(",]", "]")

    return json.loads(json_str)


# ================== AI COMPARISON FUNCTION ==================
def compare_resume_jd_with_ai(resume_data: dict, jd_data: dict) -> dict:
    """
    Use Groq LLM to compare resume and job description intelligently.
    """

    prompt = f"""
You are an expert HR consultant and resume analyst.

RESUME DATA:
{json.dumps(resume_data, indent=2)}

JOB DESCRIPTION DATA:
{json.dumps(jd_data, indent=2)}

Return ONLY valid JSON with this schema:

{{
    "match_score": <number 0-100>,
    "missing_skills": [],
    "missing_tools": [],
    "missing_keywords": [],
    "strengths": [],
    "recommendations": [],
    "experience_gap": "",
    "overall_assessment": ""
}}

Rules:
- Strict JSON only
- No explanation text outside JSON
- No trailing commas
- Be specific and actionable
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON generator. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    raw_output = completion.choices[0].message.content.strip()

    return safe_json_extract(raw_output)


# ================== MAIN RECOMMENDATION ENGINE ==================
def generate_recommendations(resume_data: dict, jd_data: dict) -> dict:
    """
    Generate AI-powered resume recommendations.
    """

    if not jd_data:
        raise ValueError("Job description data is required.")

    try:
        ai_analysis = compare_resume_jd_with_ai(resume_data, jd_data)
    except Exception as e:
        return {
            "resume_name": resume_data.get("name"),
            "resume_email": resume_data.get("email"),
            "error": f"AI analysis failed: {str(e)}",
            "analysis_method": "AI-powered"
        }

    resume_score = float(ai_analysis.get("match_score", 0))
    is_below_threshold = resume_score < THRESHOLD_SCORE

    output = {
        "resume_name": resume_data.get("name"),
        "resume_email": resume_data.get("email"),
        "resume_score": round(resume_score, 2),
        "threshold": THRESHOLD_SCORE,
        "is_below_threshold": is_below_threshold,
        "threshold_met": not is_below_threshold,
        "missing_skills": ai_analysis.get("missing_skills", []),
        "missing_tools": ai_analysis.get("missing_tools", []),
        "missing_keywords": ai_analysis.get("missing_keywords", []),
        "strengths": ai_analysis.get("strengths", []),
        "recommendations": ai_analysis.get("recommendations", []),
        "experience_gap": ai_analysis.get("experience_gap", ""),
        "overall_assessment": ai_analysis.get("overall_assessment", ""),
        "analysis_method": "AI-powered"
    }

    return output


# ================== TEST RUN ==================
if __name__ == "__main__":
    sample_resume = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "skills": ["Python", "Flask", "REST API"],
        "tools": ["Git", "Docker"],
        "experience_years": 4
    }

    sample_jd = {
        "skills": ["Python", "Django", "REST API", "PostgreSQL"],
        "tools": ["Git", "Docker", "Jenkins"],
        "experience_years": 5,
        "keywords": ["Machine Learning", "Microservices"]
    }

    result = generate_recommendations(sample_resume, sample_jd)
    print(json.dumps(result, indent=2))
