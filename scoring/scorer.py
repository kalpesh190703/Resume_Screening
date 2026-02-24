import json
import sys

def calculate_scores(resume_data, jd_data, threshold):
    """
    Calculates similarity scores between a resume and a job description.
    
    Weights:
    - 40% Skill match
    - 10% Tools match
    - 30% Experience match
    - 20% Keyword relevance
    """
    
    # helper to clean and get sets
    def get_set(data, key):
        items = data.get(key, [])
        if isinstance(items, str):
            items = [items]
        return set([str(i).lower().strip() for i in items])

    # 1. Skill Match (40%)
    resume_skills = get_set(resume_data, 'skills')
    jd_skills = get_set(jd_data, 'skills')
    
    if not jd_skills:
        skill_score = 1.0
        missing_skills = []
    else:
        matched_skills = resume_skills.intersection(jd_skills)
        skill_score = len(matched_skills) / len(jd_skills)
        missing_skills = list(jd_skills - matched_skills)
    
    # 2. Tools Match (10%)
    resume_tools = get_set(resume_data, 'tools')
    jd_tools = get_set(jd_data, 'tools')
    
    if not jd_tools:
        tools_score = 1.0
    else:
        matched_tools = resume_tools.intersection(jd_tools)
        tools_score = len(matched_tools) / len(jd_tools)

    # 3. Experience Match (30%)
    # Support both "experience years" and "experience_years"
    resume_exp = resume_data.get('experience_years') or resume_data.get('experience years', 0)
    jd_min_exp = jd_data.get('experience_years') or jd_data.get('experience years', 0)
    
    if jd_min_exp == 0:
        exp_score = 1.0
    else:
        # Score is capped at 1.0
        exp_score = min(1.0, float(resume_exp) / float(jd_min_exp))
        
    # 4. Keyword Relevance (20%)
    # Extract keywords from JD if present, else use JD skills/tools as keywords
    jd_keywords = get_set(jd_data, 'keywords')
    if not jd_keywords:
        # Fallback: if no specific keywords field, use a combination of skills
        jd_keywords = jd_skills.union(jd_tools)

    if not jd_keywords:
        keyword_score = 1.0
    else:
        # Create a search blob from resume
        search_blob = " ".join([
            str(resume_data.get('name', "")),
            str(resume_data.get('education', "")),
            " ".join(resume_data.get('skills', [])),
            " ".join(resume_data.get('tools', []))
        ]).lower()
        
        matched_keywords = [k for k in jd_keywords if k in search_blob]
        keyword_score = len(matched_keywords) / len(jd_keywords) if jd_keywords else 1.0
        
    # Weighted Scoring Breakdown
    # 40% Skills, 10% Tools, 30% Experience, 20% Keywords
    final_score = (skill_score * 0.40) + \
                  (tools_score * 0.10) + \
                  (exp_score * 0.30) + \
                  (keyword_score * 0.20)
    
    final_percentage = final_score * 100
    
    return {
        "resume_score": round(final_percentage, 2),
        "jd_score": 100.0, # JD is the baseline
        "missing_skills": missing_skills,
        "is_above_threshold": final_percentage >= threshold,
        "details": {
            "skill_match": round(skill_score * 100, 2),
            "tools_match": round(tools_score * 100, 2),
            "experience_match": round(exp_score * 100, 2),
            "keyword_relevance": round(keyword_score * 100, 2)
        }
    }

def main():
    if len(sys.argv) < 4:
        print("Usage: python scorer.py <resume_json_path> <jd_json_path> <threshold_percentage>")
        sys.exit(1)
        
    resume_path = sys.argv[1]
    jd_path = sys.argv[2]
    try:
        threshold = float(sys.argv[3])
    except ValueError:
        print("Error: Threshold must be a number.")
        sys.exit(1)
        
    try:
        with open(resume_path, 'r') as f:
            resume_data = json.load(f)
        with open(jd_path, 'r') as f:
            jd_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        sys.exit(1)
        
    results = calculate_scores(resume_data, jd_data, threshold)
    
    # Formatting output as requested
    output = {
        "Resume score": f"{results['resume_score']}%",
        "JD score": f"{results['jd_score']}%",
        "missing_skills": results['missing_skills'],
        "threshold_met": results['is_above_threshold'],
        "details": results['details']
    }
    
    print("\n--- Similarity Calculation Results ---")
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    main()
