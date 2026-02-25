# import json
# import sys
# import os
# from dotenv import load_dotenv
# from groq import Groq

# # ================== ENV SETUP ==================
# load_dotenv()
# api_key = os.getenv("GROQ_API_KEY")

# client = None
# if api_key:
#     try:
#         client = Groq(api_key=api_key)
#     except Exception:
#         client = None


# # ================== SAFE JSON PARSER ==================
# def safe_json_extract(raw: str) -> dict:
#     start = raw.find("{")
#     end = raw.rfind("}") + 1
#     if start == -1 or end == -1:
#         raise ValueError("No JSON found in LLM response")
#     return json.loads(raw[start:end])


# # ================== LLM SEMANTIC MATCHING ==================
# def get_matches_with_llm(resume_items, jd_items, item_type="skills"):
#     if not jd_items:
#         return set(), []

#     resume_items = [str(i).strip() for i in resume_items if i]
#     jd_items = [str(i).strip() for i in jd_items if i]

#     # ---------- Fallback: exact match ----------
#     if not client:
#         resume_set = {i.lower() for i in resume_items}
#         matched = [i for i in jd_items if i.lower() in resume_set]
#         missing = [i for i in jd_items if i not in matched]
#         return set(matched), missing

#     prompt = f"""
# You are an ATS semantic matching engine.

# TASK:
# Match REQUIRED {item_type} from a Job Description against a Candidate profile.

# RULES:
# - Return ONLY items that appear in REQUIRED list
# - Semantic matches allowed (e.g., SQL ↔ PostgreSQL)
# - Do NOT invent new skills
# - Missing tools should be penalized less than missing skills

# Candidate {item_type}: {", ".join(resume_items)}
# Required {item_type}: {", ".join(jd_items)}

# Return STRICT JSON ONLY:
# {{
#   "matched": [],
#   "missing": []
# }}
# """

#     try:
#         response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             response_format={"type": "json_object"},
#             temperature=0.1
#         )

#         result = safe_json_extract(response.choices[0].message.content)

#         matched = set()
#         jd_map = {i.lower(): i for i in jd_items}

#         for item in result.get("matched", []):
#             key = item.lower().strip()
#             if key in jd_map:
#                 matched.add(jd_map[key])

#         missing = [i for i in jd_items if i not in matched]
#         return matched, missing

#     except Exception:
#         resume_set = {i.lower() for i in resume_items}
#         matched = [i for i in jd_items if i.lower() in resume_set]
#         missing = [i for i in jd_items if i not in matched]
#         return set(matched), missing


# # ================== SCORE ENGINE ==================
# def calculate_scores(resume_data, jd_data, threshold):

#     def get_list(data, key):
#         val = data.get(key, [])
#         if isinstance(val, str):
#             return [val.strip()]
#         return [str(v).strip() for v in val if v]

#     # ---------- SKILLS (45%) ----------
#     resume_skills = get_list(resume_data, "skills")
#     jd_skills = get_list(jd_data, "skills")

#     if jd_skills:
#         matched_skills, missing_skills = get_matches_with_llm(
#             resume_skills, jd_skills, "skills"
#         )
#         skill_coverage = len(matched_skills) / len(jd_skills)
#     else:
#         skill_coverage = 1.0
#         missing_skills = []

#     # ---------- TOOLS (10%) ----------
#     resume_tools = get_list(resume_data, "tools")
#     jd_tools = get_list(jd_data, "tools")

#     if jd_tools:
#         matched_tools, _ = get_matches_with_llm(
#             resume_tools, jd_tools, "tools"
#         )
#         tools_coverage = len(matched_tools) / len(jd_tools)
#     else:
#         tools_coverage = 1.0

#     # ---------- EXPERIENCE (25%) ----------
#     resume_exp = float(resume_data.get("experience_years", 0))
#     jd_exp = float(jd_data.get("experience_years", 0))

#     if jd_exp > 0:
#         exp_coverage = min(1.0, resume_exp / jd_exp)
#     else:
#         exp_coverage = 1.0

#     # ---------- KEYWORDS (20%) ----------
#     jd_keywords = get_list(jd_data, "keywords") or jd_skills + jd_tools
#     resume_context = resume_skills + resume_tools + [
#         resume_data.get("education", "")
#     ]

#     if jd_keywords:
#         matched_kw, _ = get_matches_with_llm(
#             resume_context, jd_keywords, "keywords"
#         )
#         keyword_coverage = len(matched_kw) / len(jd_keywords)
#     else:
#         keyword_coverage = 1.0

#     # ---------- FINAL SCORE ----------
#     raw_score = (
#         skill_coverage * 0.55 +
#         tools_coverage * 0.10 +
#         exp_coverage * 0.25 +
#         keyword_coverage * 0.10
#     )

#     final_score = raw_score * 100

#     # ---------- SOFT FLOOR (CRITICAL FIX) ----------
#     if skill_coverage >= 0.70 and final_score < 70:
#         final_score = 70 + (skill_coverage - 0.70) * 30

#     final_score = round(min(final_score, 100), 2)

#     return {
#         "resume_score": final_score,
#         "is_above_threshold": final_score >= threshold,
#         "missing_skills": missing_skills,
#         "details": {
#             "skill_match": round(skill_coverage * 100, 2),
#             "tools_match": round(tools_coverage * 100, 2),
#             "experience_match": round(exp_coverage * 100, 2),
#             "keyword_relevance": round(keyword_coverage * 100, 2),
#         }
#     }


# # ================== CLI TEST ==================
# if __name__ == "__main__":
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     output_dir = os.path.join(base_dir, "data", "output")

#     threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 70

#     with open(os.path.join(output_dir, "jd.json"), "r") as f:
#         jd_data = json.load(f)

#     for file in os.listdir(output_dir):
#         if file.endswith(".json") and file != "jd.json":
#             with open(os.path.join(output_dir, file)) as f:
#                 resume_data = json.load(f)

#             result = calculate_scores(resume_data, jd_data, threshold)
#             print(f"\n=== SCORE FOR {file} ===")
#             print(json.dumps(result, indent=2))

import json
import os
import sys
from dotenv import load_dotenv
from groq import Groq

# ================== ENV ==================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ================== SAFE JSON ==================
def safe_json_extract(raw: str) -> dict:
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == -1:
        raise ValueError("No JSON in response")
    return json.loads(raw[start:end])


# ================== LLM SEMANTIC SCORER ==================
def llm_semantic_score(resume_data, jd_data):
    """
    Pure semantic scoring.
    NO math. NO ratios. LLM decides.
    """

    prompt = f"""
You are a senior technical recruiter.

GOAL:
Judge how strictly the candidate matches the job requirements.

STRICT RULES:
- Missing any core/required skill or technology should result in a LOW score (below 60).
- Missing required experience should result in a LOW score (below 60).
- Only candidates with ALL core skills and experience should get 80+.
- Do NOT boost scores for partial matches or trainable skills.
- Penalize missing frameworks, languages, or platforms heavily.
- Only minor tools (e.g., editors, basic utilities) can be considered trainable.
- Be harsh: if in doubt, score lower.

SCORING SCALE (VERY STRICT):
90–100 : Perfect match (all core skills, all experience)
75–89  : Strong match (only minor/optional skills missing)
60–74  : Moderate (missing some required skills or experience)
40–59  : Weak (missing multiple core skills or experience)
Below 40: Poor (major gaps)

Resume JSON:
{json.dumps(resume_data, indent=2)}

Job Description JSON:
{json.dumps(jd_data, indent=2)}

Return ONLY valid JSON:
{{
    "score": number,
    "domain_match": "yes | partial | no",
    "missing_critical_skills": [],
    "missing_trainable_skills": [],
    "missing_experience": "<analysis of experience gap>",
    "overall_reasoning": ""
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1
    )

    return safe_json_extract(response.choices[0].message.content)


# ================== FINAL SCORE ENGINE ==================
def calculate_scores(resume_data, jd_data, threshold):
    # --- Helper to get list ---
    def get_list(data, key):
        val = data.get(key, [])
        if isinstance(val, str):
            return [val.strip()]
        return [str(v).strip() for v in val if v]

    # --- Skills (50%) ---
    resume_skills = get_list(resume_data, "skills")
    jd_skills = get_list(jd_data, "skills")
    if jd_skills:
        matched_skills = [s for s in resume_skills if s in jd_skills]
        skill_coverage = len(matched_skills) / len(jd_skills)
        missing_skills = [s for s in jd_skills if s not in resume_skills]
    else:
        skill_coverage = 1.0
        missing_skills = []

    # --- Tools (10%) ---
    resume_tools = get_list(resume_data, "tools")
    jd_tools = get_list(jd_data, "tools")
    if jd_tools:
        matched_tools = [t for t in resume_tools if t in jd_tools]
        tools_coverage = len(matched_tools) / len(jd_tools)
        missing_tools = [t for t in jd_tools if t not in resume_tools]
    else:
        tools_coverage = 1.0
        missing_tools = []

    # --- Experience (10%) ---
    resume_exp = float(resume_data.get("experience_years", 0))
    jd_exp = float(jd_data.get("experience_years", 0))
    if jd_exp > 0:
        exp_coverage = min(1.0, resume_exp / jd_exp)
    else:
        exp_coverage = 1.0

    # --- Education (10%) ---
    resume_edu = resume_data.get("education", "").strip().lower()
    jd_edu = jd_data.get("education", "").strip().lower()
    if jd_edu:
        edu_coverage = 1.0 if jd_edu in resume_edu else 0.0
    else:
        edu_coverage = 1.0

    # --- Keywords (20%) ---
    jd_keywords = get_list(jd_data, "keywords")
    resume_text = " ".join(resume_skills + resume_tools + [resume_edu])
    if jd_keywords:
        matched_keywords = [k for k in jd_keywords if k.lower() in resume_text.lower()]
        keyword_coverage = len(matched_keywords) / len(jd_keywords)
    else:
        keyword_coverage = 1.0

    # --- Final Score (updated weights) ---
    final_score = (
        skill_coverage * 0.60 +
        exp_coverage * 0.20 +
        edu_coverage * 0.10 +
        tools_coverage * 0.05 +
        keyword_coverage * 0.05
    ) * 100
    final_score = round(min(final_score, 100), 2)

    return {
        "resume_score": final_score,
        "is_above_threshold": final_score >= threshold,
        "missing_skills": missing_skills,
        "missing_tools": missing_tools,
        "details": {
            "skill_match": round(skill_coverage * 100, 2),
            "tools_match": round(tools_coverage * 100, 2),
            "experience_match": round(exp_coverage * 100, 2),
            "education_match": round(edu_coverage * 100, 2),
            "keyword_relevance": round(keyword_coverage * 100, 2),
        }
    }


# ================== CLI TEST ==================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data", "output")

    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 70

    with open(os.path.join(output_dir, "jd.json")) as f:
        jd_data = json.load(f)

    for file in os.listdir(output_dir):
        if file.endswith(".json") and file != "jd.json":
            with open(os.path.join(output_dir, file)) as f:
                resume_data = json.load(f)

            result = calculate_scores(resume_data, jd_data, threshold)
            print(f"\n=== SCORE FOR {file} ===")
            print(json.dumps(result, indent=2))