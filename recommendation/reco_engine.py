# reco_engine.py
import json

THRESHOLD_SCORE = 70.0  # percent threshold for triggering recommendations

def generate_recommendations(resume_data, jd_data=None):
    """
    Generate missing skills, tools, keywords, and improvement suggestions
    for a resume based on JD.
    
    Parameters:
        resume_data (dict): Resume info from Task 4 including score, skills, tools, experience
        jd_data (dict): Job description data from Task 4
    
    Returns:
        dict: Recommendations JSON for this resume
    """
    # Use jd_data from resume_data if not provided separately
    if jd_data is None:
        jd_data = resume_data.get("jd_data", {})

    # --- Extract relevant info ---
    resume_skills = set(resume_data.get("skills", []))
    resume_tools = set(resume_data.get("tools", []))
    resume_keywords = set(resume_data.get("keywords", []))
    resume_experience = resume_data.get("experience_years", 0)

    jd_skills = set(jd_data.get("skills", []))
    jd_tools = set(jd_data.get("tools", []))
    jd_keywords = set(jd_data.get("keywords", []))
    jd_experience = jd_data.get("experience_years", 0)

    # --- Identify missing items ---
    missing_skills = list(jd_skills - resume_skills)
    missing_tools = list(jd_tools - resume_tools)
    missing_keywords = list(jd_keywords - resume_keywords)

    # --- Generate recommendations ---
    recommendations = []
    for skill in missing_skills:
        recommendations.append(f"Include experience with '{skill}' in your resume.")
    for tool in missing_tools:
        recommendations.append(f"Highlight your experience with '{tool}'.")
    for kw in missing_keywords:
        recommendations.append(f"Add relevant keyword '{kw}' from the job description.")

    # Check experience
    if resume_experience < jd_experience:
        recommendations.append(
            f"Highlight more relevant experience (current: {resume_experience} yrs, required: {jd_experience} yrs)."
        )

    # Convert Resume score to float if exists
    score_str = str(resume_data.get("Resume score", "0")).replace("%", "")
    try:
        resume_score = float(score_str)
    except ValueError:
        resume_score = 0.0

    # Flag if below threshold
    is_below_threshold = resume_score < THRESHOLD_SCORE

    if is_below_threshold and not recommendations:
        recommendations.append("Resume score is low. Review and enhance skills, tools, and experience.")

    # --- Prepare structured output ---
    output = {
        "resume_name": resume_data.get("name"),
        "resume_email": resume_data.get("email"),
        "resume_score": round(resume_score, 2),
        "threshold": THRESHOLD_SCORE,
        "is_below_threshold": is_below_threshold,
        "missing_skills": missing_skills,
        "missing_tools": missing_tools,
        "missing_keywords": missing_keywords,
        "recommendations": recommendations,
        "details": {
            "skill_match": resume_data.get("details", {}).get("skill_match", 0),
            "tools_match": resume_data.get("details", {}).get("tools_match", 0),
            "experience_match": resume_data.get("details", {}).get("experience_match", 0),
            "keyword_relevance": resume_data.get("details", {}).get("keyword_relevance", 0)
        }
    }

    return output