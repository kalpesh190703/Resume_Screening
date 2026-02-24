import json
import sys

def calculate_scores(resume_data, jd_data, threshold):
    """
    Calculates similarity scores between a resume and a job description.
    
    Weights:
    - 50% Skill match
    - 30% Experience match
    - 20% Keyword relevance
    """
    
    # 1. Skill Match (50%)
    resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
    jd_skills = set([s.lower() for s in jd_data.get('skills', [])])
    
    if not jd_skills:
        skill_score = 1.0
        missing_skills = []
    else:
        matched_skills = resume_skills.intersection(jd_skills)
        skill_score = len(matched_skills) / len(jd_skills)
        missing_skills = list(jd_skills - matched_skills)
    
    # 2. Experience Match (30%)
    resume_exp = resume_data.get('experience_years', 0)
    jd_min_exp = jd_data.get('min_experience_years', 0)
    
    if jd_min_exp == 0:
        exp_score = 1.0
    else:
        exp_score = min(1.0, resume_exp / jd_min_exp)
        
    # 3. Keyword Relevance (20%)
    # Keywords can be checked in skills, education, and potentially other fields
    jd_keywords = set([k.lower() for k in jd_data.get('keywords', [])])
    if not jd_keywords:
        keyword_score = 1.0
    else:
        # Check presence in skills, name, email (unlikely), education
        search_text = " ".join(resume_data.get('skills', [])) + " " + \
                      resume_data.get('education', "") + " " + \
                      resume_data.get('name', "")
        search_text = search_text.lower()
        
        matched_keywords = [k for k in jd_keywords if k in search_text]
        keyword_score = len(matched_keywords) / len(jd_keywords)
        
    # Weighted Scoring
    weighted_score = (skill_score * 0.5) + (exp_score * 0.3) + (keyword_score * 0.2)
    final_percentage = weighted_score * 100
    
    return {
        "resume_score": round(final_percentage, 2),
        "missing_skills": missing_skills,
        "is_above_threshold": final_percentage >= threshold,
        "details": {
            "skill_match": round(skill_score * 100, 2),
            "experience_match": round(exp_score * 100, 2),
            "keyword_relevance": round(keyword_score * 100, 2)
        }
    }

def main():
    if len(sys.argv) < 4:
        print("Usage: python resume_scorer.py <resume_json_path> <jd_json_path> <threshold_percentage>")
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
    
    output = {
        "candidate_name": resume_data.get('name', "Unknown"),
        "skill_match_percentage": results['details']['skill_match'],
        "experience_match_percentage": results['details']['experience_match'],
        "keyword_relevance_score": results['details']['keyword_relevance'],
        "final_score": results['resume_score'],
        "missing_skills": results['missing_skills'],
        "threshold": threshold,
        "status": "Passed" if results['is_above_threshold'] else "Failed"
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
