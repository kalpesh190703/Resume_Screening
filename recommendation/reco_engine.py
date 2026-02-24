# reco_engine.py
import os
import json
from dotenv import load_dotenv
from groq import Groq

# ================== SETUP ==================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

THRESHOLD_SCORE = 70.0  # percent threshold for triggering recommendations


# ================== SAFE JSON PARSER ==================
def safe_json_extract(raw):
    """Extract JSON from raw LLM response."""
    start = raw.find("{")
    end = raw.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError(f"No JSON found:\n{raw}")

    json_str = raw[start:end]
    json_str = json_str.replace(",}", "}").replace(",]", "]")
    return json.loads(json_str)


# ================== AI-POWERED COMPARISON ==================
def compare_resume_jd_with_ai(resume_data, jd_data):
    """
    Use Groq API to intelligently compare resume with JD and generate
    detailed analysis and recommendations.
    """
    prompt = f"""
You are an expert HR consultant and resume analyst. Compare the following resume data with the job description and provide a detailed analysis.

RESUME DATA:
{json.dumps(resume_data, indent=2)}

JOB DESCRIPTION DATA:
{json.dumps(jd_data, indent=2)}

Analyze the match and return ONLY a JSON object with this exact schema:
{{
    "match_score": <number 0-100>,
    "missing_skills": [<list of skills from JD not in resume>],
    "missing_tools": [<list of tools from JD not in resume>],
    "missing_keywords": [<list of important keywords from JD not in resume>],
    "strengths": [<list of strong matches between resume and JD>],
    "recommendations": [<list of specific actionable improvements>],
    "experience_gap": "<analysis of experience alignment>",
    "overall_assessment": "<brief summary of candidacy fit>"
}}

Be specific and actionable in your recommendations. Focus on what would make the biggest impact.
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator and expert resume analyst.\n"
                    "Return ONLY valid JSON.\n"
                    "Rules:\n"
                    "- All keys must be in double quotes\n"
                    "- No trailing commas\n"
                    "- No comments\n"
                    "- No explanation text outside JSON\n"
                    "- Be specific and actionable in recommendations"
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw = completion.choices[0].message.content.strip()
    return safe_json_extract(raw)



# ================== MAIN RECOMMENDATION ENGINE ==================
def generate_recommendations(resume_data, jd_data=None, use_ai=True):
    """
    Generate missing skills, tools, keywords, and improvement suggestions
    for a resume based on JD using AI-powered analysis.
    
    Parameters:
        resume_data (dict): Resume info including skills, tools, experience
        jd_data (dict): Job description data
        use_ai (bool): Whether to use Groq API for intelligent comparison
    
    Returns:
        dict: Comprehensive recommendations JSON for this resume
    """
    # Use jd_data from resume_data if not provided separately
    if jd_data is None:
        jd_data = resume_data.get("jd_data", {})

    ai_analysis = compare_resume_jd_with_ai(resume_data, jd_data)
    
    # Get match score from AI analysis
    resume_score = ai_analysis.get("match_score", 0)
    is_below_threshold = resume_score < THRESHOLD_SCORE

    # --- Prepare structured output ---
    output = {
        "resume_name": resume_data.get("name"),
        "resume_email": resume_data.get("email"),
        "resume_score": round(resume_score, 2),
        "threshold": THRESHOLD_SCORE,
        "is_below_threshold": is_below_threshold,
        "missing_skills": ai_analysis.get("missing_skills", []),
        "missing_tools": ai_analysis.get("missing_tools", []),
        "missing_keywords": ai_analysis.get("missing_keywords", []),
        "strengths": ai_analysis.get("strengths", []),
        "recommendations": ai_analysis.get("recommendations", []),
        "experience_gap": ai_analysis.get("experience_gap", ""),
        "overall_assessment": ai_analysis.get("overall_assessment", ""),
        "analysis_method": "AI-powered" if use_ai else "Basic"
    }

    return output


# ================== CLI / TEST ==================
if __name__ == "__main__":
    # Load sample data for testing
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resume_path = os.path.join(base_dir, "data", "output", "resume.json")
    jd_path = os.path.join(base_dir, "data", "output", "jd.json")
    
    if os.path.exists(resume_path) and os.path.exists(jd_path):
        with open(resume_path, "r") as f:
            resume = json.load(f)
        with open(jd_path, "r") as f:
            jd = json.load(f)
        
        print("🔍 Analyzing resume against job description...\n")
        result = generate_recommendations(resume, jd)
        print(json.dumps(result, indent=2))
    else:
        print("❌ Could not find resume.json or jd.json in data/output/")
        print(f"   Expected: {resume_path}")
        print(f"   Expected: {jd_path}")